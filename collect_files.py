import time
import os
import sys
from pathlib import Path
from typing import Generator, List, Optional, Tuple, Dict
import fnmatch
from collections import defaultdict



def read_gitignore(gitignore_path: Path, addignore:list[str]) -> Dict[str, List[str]]:
    lines = []
    if gitignore_path.exists() and gitignore_path.is_file():
        with open(gitignore_path, 'r') as file:
            lines = file.readlines()
    lines.extend(addignore)
    patterns = defaultdict(list)
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            if line.endswith('/'):
                patterns['directories'].append(line[:-1])
            else:
                patterns['files'].append(line)
    return patterns

def skip_item(path: Path, root_dir: Path, patterns: Dict[str, List[str]]) -> bool:
    rel_path_str = str(path.relative_to(root_dir))
    if path.is_dir():
        for pattern in patterns['directories']:
            if fnmatch.fnmatch(rel_path_str, pattern) or fnmatch.fnmatch(rel_path_str, pattern + '/*'):
                return True
    elif path.is_file():
        for pattern in patterns['files']:
            if fnmatch.fnmatch(rel_path_str, pattern):             
                return True
    return False

def find_recursive( root_dir: Path, 
                    patterns: Dict[str, List[str]]
                    )    -> Generator[tuple[Path, os.stat_result], None, None]:
    for path in root_dir.iterdir():
        if path.is_dir():
            if skip_item(path, root_dir, patterns):
                continue
            yield from find_recursive(path, patterns)
        elif path.is_file() and not skip_item(path, root_dir, patterns):
            yield path, path.stat()


def find_files(root_dir: Path,
               addignore:list[str]
               ) -> list[tuple[Path, os.stat_result]]:
    gitignore_path = root_dir / '.gitignore' 
    patterns = read_gitignore(gitignore_path, addignore)
    fileinfo = list(find_recursive(root_dir, patterns))
    return fileinfo




if __name__ == "__main__":
    root_dir = Path(sys.argv[1])  # Beispiel für einen vollständigen Pfad
    try:
        filst = find_files( root_dir,['.git/','bin/'])
        if len(filst):
            found = filst[0]
            for fi in filst[1:]:
                if fi[1].st_mtime > found[1].st_mtime:
                    found = fi
            print(f"The latest modified file is: {str(found[0])}")
            print(f"Last modified time: {time.ctime(found[1].st_mtime)}")
        else:
            print('no files found')

    except FileNotFoundError as e:
        print(e)