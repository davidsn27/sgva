import pathlib

p = pathlib.Path(__file__).resolve().parent.parent
for f in p.rglob("*.py"):
    s = f.read_text(encoding="utf-8")
    ns = "\n".join([line.rstrip() for line in s.splitlines()])
    if ns != s:
        f.write_text(ns, encoding="utf-8")
print("stripped")
