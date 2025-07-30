import os
import argparse

dir_color = "\033[94m"  
file_color = "\033[92m"   
normal = "\033[0m"
def listing(path, pre = ""):
    
    content = os.listdir(path)
    for i, entry in enumerate(content):
        full = os.path.join(path,entry)
        viz = "└── " if i == len(content) - 1 else "├── "
        color = dir_color if os.path.isdir(full) else file_color
        print(normal + pre + viz + color + entry + normal )
        if os.path.isdir(full):
            next = pre + ("    " if i == len(content) - 1 else "|  ")
            listing(full, next)
def list_folder_only(path, pre = ""):
     content = os.listdir(path)
     folders = [i for i in content if os.path.isdir(os.path.join(path, i))]
     for i, entry in enumerate(folders):
        full = os.path.join(path,entry)
        viz = "└── " if i == len(folders) - 1 else "├── "
        print(normal + pre + viz + dir_color + entry + normal )
        next = pre + ("    " if i == len(folders) - 1 else "|  ")
        list_folder_only(full, next)

def main(): 
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", help="Path to visualize")
    parser.add_argument("-f", "--folders", action="store_true", help="Show only folders")
    args = parser.parse_args()

    path = os.path.abspath(os.path.expanduser(args.path))
    
    if not os.path.exists(path):
        print(f"Error: Path '{path}' does not exist")
        return 1
    
    if not os.path.isdir(path):
        print(f"Error: '{path}' is not a directory")
        return 1
    
    print(f"{dir_color}{path}{normal}")
    
    if args.folders:
        list_folder_only(path)
    else:
        listing(path)
    
    return 0

if __name__ == "__main__":
    exit(main())