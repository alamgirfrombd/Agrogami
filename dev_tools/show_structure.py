import os

IGNORE = ["venv", "__pycache__", ".git", ".idea"]

def tree(path):
    for root, dirs, files in os.walk(path):
        # Remove ignored folders
        dirs[:] = [d for d in dirs if d not in IGNORE]
        level = root.count(os.sep)
        indent = " " * 4 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 4 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")

tree(".")
