import time
import sys
from pathlib import Path
from collect_files import find_files



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