import sys

name = sys.argv[1]
seg = sys.argv[2]
link = sys.argv[3]
icon = "Shrine" if len(sys.argv) < 5 else sys.argv[4]
profile = "shrine_clean" if len(sys.argv) < 6 else sys.argv[5]
with open(f"segments/{seg}.toml", "w+", encoding="utf-8") as file:
    file.write(f"link = \"{link}\"\n")
    file.write(f"runner = \"{name}\"\n")
    file.write(f"icon = \"{icon}\"\n")
    file.write(f"profile = \"{profile}\"\n")
