import sys
import hashlib
import os

BUF_SIZE = 65536
def add_file(sha, file_path) -> bool:
    if not os.path.isfile(file_path):
        return False
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha.update(data)
    return True


def test_files(hash_path, file_paths: list[str], update=False) -> bool:
    if os.path.isfile(hash_path):
        with open(hash_path, "r", encoding="utf-8") as hash_file:
            current_digest = hash_file.read().rstrip()
    else:
        current_digest = ""
    if not current_digest and not update:
        return False
        
    err = False
    sha = hashlib.sha512()
    for file_path in file_paths:
        if not add_file(sha, file_path):
            err = True
            break
    new_digest = sha.hexdigest() if not err else ""
    if current_digest != new_digest:
        if update:
            with open(hash_path, "w+", encoding="utf-8") as hash_file:
                hash_file.write(new_digest)
    
    return bool(current_digest) and current_digest == new_digest
                
if __name__ == "__main__":
    sha = hashlib.sha512()
    add_file(sha, sys.argv[1])
    print(sha.hexdigest())
