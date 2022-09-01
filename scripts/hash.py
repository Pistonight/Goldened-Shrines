import sys
import hashlib
import os

BUF_SIZE = 65536
def add_file(sha, file_path):
    if os.path.isfile(file_path):
        sha.update(b"1")
        sha.update(bytes(file_path, encoding="utf-8"))
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha.update(data)
    else:
        sha.update(b"0")
        sha.update(bytes(file_path, encoding="utf-8"))
   

def test_files(hash_path, file_paths: list[str], update=False) -> bool:
    if os.path.isfile(hash_path):
        with open(hash_path, "r", encoding="utf-8") as hash_file:
            current_digest = hash_file.read().rstrip()
    else:
        current_digest = ""
    sha = hashlib.sha512()
    for file_path in file_paths:
        add_file(sha, file_path)
    new_digest = sha.hexdigest()
    if current_digest != new_digest:
        if update:
            with open(hash_path, "w+", encoding="utf-8") as hash_file:
                hash_file.write(new_digest)
        return False
    return True
                
if __name__ == "__main__":
    sha = hashlib.sha512()
    add_file(sha, sys.argv[1])
    print(sha.hexdigest())
