import os

# Directories to skip
SKIP_DIRS = {'node_modules', '.git', 'venv', '.idea', '__pycache__'}

def list_files(startpath):
    for root, dirs, files in os.walk(startpath, topdown=True):
        # Remove directories in SKIP_DIRS
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")

if __name__ == "__main__":
    # Set the directory you want to start from
    rootDir = '.'
    list_files(rootDir)
