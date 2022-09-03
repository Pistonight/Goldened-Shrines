
def generate_index_html():
    lines: list[str] = []
    with open("docs/index.html", "r", encoding="utf-8") as file:
        for line in file:
            lines.append(line)
    with open("docs/index.html", "w", encoding="utf-8") as file:
        skip_until = None
        for line in lines:
            if skip_until is not None and not line.startswith(skip_until):
                continue
            skip_until = None
            file.write(line)
            if line.startswith("<!-- GENERATOR METATITLE -->"):
                