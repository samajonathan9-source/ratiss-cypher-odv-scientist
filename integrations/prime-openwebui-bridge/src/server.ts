import { createServer, type IncomingMessage, type ServerResponse } from 'node:http';
import { spawn, type ChildProcessWithoutNullStreams } from 'node:child_process';
import { randomUUID } from 'node:crypto';

const port = Number(process.env.PORT ?? 8787);
const host = process.env.HOST ?? '127.0.0.1';
const primeBin = process.env.PRIME_AGENT_BIN ?? 'prime-agent';
const ratissRunner = new URL('./ratiss_runner.py', import.meta.url).pathname;
const pythonBin = process.env.PYTHON_BIN ?? 'python3';
const subscribers = new Set<ServerResponse>();
let prime: ChildProcessWithoutNullStreams | undefined;
let ratiss: ChildProcessWithoutNullStreams | undefined;
let active:
  | {
      response?: ServerResponse;
      stream: boolean;
      text: string;
      model: string;
    }
  | undefined;

function json(res: ServerResponse, status: number, value: unknown) {
  res.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'access-control-allow-origin': '*',
  });
  res.end(JSON.stringify(value));
}

function sseHeaders(res: ServerResponse) {
  res.writeHead(200, {
    'content-type': 'text/event-stream; charset=utf-8',
    'cache-control': 'no-cache, no-transform',
    connection: 'keep-alive',
    'access-control-allow-origin': '*',
  });
}

function sse(res: ServerResponse, data: unknown) {
  if (!res.writableEnded) res.write(`data: ${JSON.stringify(data)}\n\n`);
}

function broadcast(event: unknown) {
  for (const subscriber of subscribers) sse(subscriber, event);
}

function startRatiss(task: string) {
  if (ratiss) ratiss.kill('SIGTERM');
  ratiss = spawn(pythonBin, [ratissRunner], { stdio: ['pipe', 'pipe', 'pipe'], env: process.env });
  let buffer = '';
  ratiss.stdout.setEncoding('utf8');
  ratiss.stdout.on('data', (chunk: string) => {
    buffer += chunk;
    let newline = buffer.indexOf('\n');
    while (newline >= 0) {
      const line = buffer.slice(0, newline).trim();
      buffer = buffer.slice(newline + 1);
      newline = buffer.indexOf('\n');
      if (!line) continue;
      try { broadcast(JSON.parse(line)); }
      catch { broadcast({ type: 'bridge_log', stream: 'ratiss', message: line }); }
    }
  });
  ratiss.stderr.setEncoding('utf8');
  ratiss.stderr.on('data', (message: string) => broadcast({ type: 'bridge_log', stream: 'ratiss-stderr', message }));
  ratiss.on('exit', (code) => {
    broadcast({ type: 'ratiss_exit', code });
    ratiss = undefined;
  });
  ratiss.stdin.write(`${JSON.stringify({ task})}\n`);
  ratiss.stdin.end();
}

function startPrime() {
  if (prime) return prime;
  prime = spawn(primeBin, ['--mode', 'rpc'], {
    stdio: ['pipe', 'pipe', 'pipe'],
    env: process.env,
  });
  let buffer = '';
  prime.stdout.setEncoding('utf8');
  prime.stdout.on('data', (chunk: string) => {
    buffer += chunk;
    let newline = buffer.indexOf('\n');
    while (newline >= 0) {
      const line = buffer.slice(0, newline).replace(/\r$/, '');
      buffer = buffer.slice(newline + 1);
      newline = buffer.indexOf('\n');
      if (!line.trim()) continue;
      try {
        handlePrimeEvent(JSON.parse(line));
      } catch {
        broadcast({ type: 'bridge_log', stream: 'stdout', message: line });
      }
    }
  });
  prime.stderr.setEncoding('utf8');
  prime.stderr.on('data', (message: string) => broadcast({ type: 'bridge_log', stream: 'stderr', message }));
  prime.on('exit', (code, signal) => {
    broadcast({ type: 'prime_exit', code, signal });
    prime = undefined;
    if (active?.response && !active.response.writableEnded) {
      if (active.stream) sse(active.response, { error: { message: 'Prime Agent process exited' } });
      active.response.end();
    }
    active = undefined;
  });
  return prime;
}

function handlePrimeEvent(event: any) {
  broadcast(event);
  if (!active) return;
  if (event.type === 'message_update' && event.assistantMessageEvent?.type === 'text_delta') {
    const delta = String(event.assistantMessageEvent.delta ?? '');
    active.text += delta;
    if (active.stream && active.response) {
      sse(active.response, {
        id: randomUUID(),
        object: 'chat.completion.chunk',
        choices: [{ index: 0, delta: { content: delta }, finish_reason: null }],
      });
    }
  }
  if (event.type === 'agent_end') {
    if (active.stream && active.response) {
      sse(active.response, {
        id: randomUUID(),
        object: 'chat.completion.chunk',
        choices: [{ index: 0, delta: {}, finish_reason: 'stop' }],
      });
      sse(active.response, '[DONE]');
      active.response.end();
    } else if (active.response) {
      json(active.response, {
        id: randomUUID(),
        object: 'chat.completion',
        model: active.model,
        choices: [{ index: 0, message: { role: 'assistant', content: active.text }, finish_reason: 'stop' }],
      });
    }
    active = undefined;
  }
}

async function body(req: IncomingMessage) {
  let data = '';
  for await (const chunk of req) data += chunk;
  return data ? JSON.parse(data) : {};
}

const server = createServer(async (req, res) => {
  if (req.method === 'OPTIONS') {
    res.writeHead(204, { 'access-control-allow-origin': '*', 'access-control-allow-methods': 'GET,POST,OPTIONS', 'access-control-allow-headers': 'content-type, authorization' });
    return res.end();
  }
  const url = new URL(req.url ?? '/', `http://${req.headers.host ?? host}`);
  if (req.method === 'GET' && url.pathname === '/health') return json(res, 200, { ok: true, primeRunning: Boolean(prime), ratissRunning: Boolean(ratiss), busy: Boolean(active) });
  if (req.method === 'GET' && url.pathname === '/v1/models') return json(res, 200, { object: 'list', data: [{ id: 'prime-agent-ratiss', object: 'model', owned_by: 'prime-intellect' }] });
  if (req.method === 'GET' && url.pathname === '/events') {
    sseHeaders(res);
    subscribers.add(res);
    sse(res, { type: 'connected' });
    req.on('close', () => subscribers.delete(res));
    return;
  }
  if (req.method === 'POST' && url.pathname === '/control/abort') {
    if (prime?.stdin.writable) prime.stdin.write(`${JSON.stringify({ type: 'abort' })}\n`);
    broadcast({ type: 'abort_requested' });
    return json(res, 200, { ok: true });
  }
  if (req.method === 'POST' && url.pathname === '/v1/chat/completions') {
    if (active) return json(res, 409, { error: { message: 'Prime Agent is already processing a task' } });
    const payload = await body(req);
    const messages = Array.isArray(payload.messages) ? payload.messages : [];
    const last = [...messages].reverse().find((message: any) => message?.role === 'user');
    const message = typeof last?.content === 'string' ? last.content : JSON.stringify(last?.content ?? '');
    if (!message) return json(res, 400, { error: { message: 'messages must contain a user message' } });
    const stream = payload.stream === true;
    if (stream) sseHeaders(res);
    active = { response: res, stream, text: '', model: String(payload.model ?? 'prime-agent-ratiss') };
    broadcast({ type: 'agent_start', source: 'open-webui' });
    startRatiss(message);
    startPrime().stdin.write(`${JSON.stringify({ type: 'prompt', message })}\n`);
    if (!stream) req.on('close', () => { if (active?.response === res) active = undefined; });
    return;
  }
  return json(res, 404, { error: { message: 'Not found' } });
});

server.listen(port, host, () => console.log(`Ratiss Prime/Open WebUI bridge listening on http://${host}:${port}`));
