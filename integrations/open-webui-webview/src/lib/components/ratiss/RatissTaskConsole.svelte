<script lang="ts">
	import { onMount } from 'svelte';

	const bridgeUrl = import.meta.env.VITE_RATISS_BRIDGE_URL ?? 'http://127.0.0.1:8787';
	let running = false;
	let expanded = false;
	let connected = false;
	let lines: string[] = [];
	let source: EventSource | undefined;
	let collapseTimer: ReturnType<typeof setTimeout> | undefined;

	function addLine(line: string) {
		lines = [...lines.slice(-80), line];
	}

	function handle(event: MessageEvent) {
		try {
			const data = JSON.parse(event.data);
			if (data.type === 'connected') {
				connected = true;
				return;
			}
			if (data.type === 'agent_start') {
				running = true;
				expanded = true;
				lines = [];
				addLine('$ prime-agent : tâche démarrée');
				return;
			}
			if (data.type === 'tool_execution_start') {
				running = true;
				expanded = true;
				addLine(`$ ${data.toolName ?? 'outil'} ${JSON.stringify(data.args ?? {})}`);
				return;
			}
			if (data.type === 'tool_execution_update') {
				const output = data.partialResult?.output ?? data.partialResult?.text ?? data.partialResult;
				if (output) addLine(String(output).slice(-500));
				return;
			}
			if (data.type === 'tool_execution_end') {
				addLine(`[${data.isError ? 'erreur' : 'terminé'}] ${data.toolName ?? 'outil'}`);
				return;
			}
			if (data.type === 'bridge_log' || data.type === 'ratiss_log') {
				addLine(`[${data.stream ?? 'log'}] ${String(data.message ?? '').trim()}`);
				return;
			}
			if (data.type === 'ratiss_route') {
				addLine(`[route] ${data.route?.detected_domain ?? 'general'} → ${data.route?.solver ?? 'cpu'}`);
				return;
			}
			if (data.type === 'ratiss_artifact') {
				addLine(`[artifact] ${data.name ?? data.path ?? 'résultat généré'}`);
				return;
			}
			if (data.type === 'ratiss_result') {
				addLine(`[validation] ${data.result?.status ?? 'résultat reçu'} · ZK=${data.result?.cryptography?.verified ?? false}`);
				return;
			}
			if (data.type === 'agent_end' || data.type === 'abort_requested') {
				running = false;
				addLine(data.type === 'agent_end' ? '$ prime-agent : tâche terminée' : '$ tâche interrompue');
				if (collapseTimer) clearTimeout(collapseTimer);
				collapseTimer = setTimeout(() => (expanded = false), 1800);
			}
		} catch {
			addLine(event.data);
		}
	}

	async function abort() {
		await fetch(`${bridgeUrl}/control/abort`, { method: 'POST' }).catch(() => undefined);
	}

	onMount(() => {
		source = new EventSource(`${bridgeUrl}/events`);
		source.onmessage = handle;
		source.onerror = () => (connected = false);
		return () => {
			source?.close();
			if (collapseTimer) clearTimeout(collapseTimer);
		};
	});
</script>

{#if running || expanded}
	<section class="fixed bottom-4 right-4 z-[100] w-[min(92vw,44rem)] overflow-hidden rounded-xl border border-gray-700 bg-gray-950/95 text-gray-100 shadow-2xl backdrop-blur">
		<header class="flex items-center justify-between border-b border-gray-800 px-4 py-3">
			<div class="flex items-center gap-2 text-sm font-medium">
				<span class:animate-pulse={running} class="h-2.5 w-2.5 rounded-full" class:bg-emerald-400={connected} class:bg-gray-600={!connected}></span>
				<span>Ratiss Linux Console</span>
				<span class="text-xs text-gray-500">{running ? 'running' : 'idle'}</span>
			</div>
			<div class="flex items-center gap-2">
				{#if running}<button class="rounded-md bg-red-500/20 px-2 py-1 text-xs text-red-300 hover:bg-red-500/30" on:click={abort}>Stop</button>{/if}
				<button class="rounded-md px-2 py-1 text-xs text-gray-400 hover:bg-gray-800" on:click={() => (expanded = !expanded)}>{expanded ? 'Hide' : 'Show'}</button>
			</div>
		</header>
		{#if expanded}
			<pre class="max-h-64 overflow-auto whitespace-pre-wrap px-4 py-3 font-mono text-xs leading-5 text-gray-300">{lines.join('\n') || '$ en attente de la prochaine tâche...'}</pre>
		{/if}
	</section>
{/if}
