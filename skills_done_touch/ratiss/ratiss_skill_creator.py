import os
import sys

def run(skill_name: str, code: str):
    """
    Crée une nouvelle skill Ratiss.
    :param skill_name: Nom de la skill (ex: ma_skill)
    :param code: Code Python de la skill
    """
    base_path = "/home/ubuntu/ratiss-cypher-odv-scientist/skills done touch/ratiss"
    file_path = os.path.join(base_path, f"{skill_name}.py")
    
    with open(file_path, "w") as f:
        f.write(code)
    
    print(f"Skill '{skill_name}' créée avec succès à l'emplacement : {file_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 ratiss_skill_creator.py <skill_name> <code>")
    else:
        run(sys.argv[1], sys.argv[2])
