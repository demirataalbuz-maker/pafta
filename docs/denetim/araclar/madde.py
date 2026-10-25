import re
import sys

kok = sys.argv[1]
nolar = [int(x) for x in sys.argv[2:]]
tablo = {}
for s in open(kok + "/DENETIM.md", encoding="utf-8").read().splitlines():
    m = re.match(r"\| (\d+) \| ([\w-]+) \| (.+?) \| (.+?) \| (.+?) \| (.*) \|$", s)
    if m:
        tablo.setdefault(int(m.group(1)), m.groups())
asama = {}
for s in open(kok + "/ASAMA2.md", encoding="utf-8").read().splitlines():
    if s.startswith("|") and not s.startswith("|---"):
        p = [x.strip() for x in re.split(r"(?<!\\)\|", s)[1:-1]]
        if len(p) >= 6:
            asama[p[0]] = p
for n in nolar:
    t = tablo.get(n)
    if not t:
        print(n, "YOK")
        continue
    print(f"=== {n} | {t[1]} | {t[2]}\n  durum: {t[5][:220]}")
    a = asama.get(t[2]) or next((v for k, v in asama.items() if k[:35] == t[2][:35]), None)
    if a:
        print("  NEDEN:", a[1][:450])
        print("  GEREKİR:", a[2][:600])
        print("  KURULUM:", a[3][:220])
