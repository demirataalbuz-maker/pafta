# -*- coding: utf-8 -*-
"""Pafta · SPL → SQLite çevirici.

Splunk Search Processing Language'in öğretilen alt kümesini SQLite SQL'e çevirir.
Her | komutu bir CTE olur ve satır sırası her aşamada gizli __sira sütunuyla
taşınır. Splunk'a sadık kalınan incelikler:

  - aramada (search) alan=değer büyük-küçük harfe duyarsızdır, * joker karakterdir;
    where/eval içinde karşılaştırmalar duyarlıdır
  - OR / AND / NOT yalnızca BÜYÜK harfle işleçtir; küçük harfle arama terimidir
  - alan!=değer alanı olmayan satırları almaz, NOT alan=değer alır
  - stats sonucu by alanlarına göre sıralanır; top/rare count ve percent üretir
  - join varsayılan olarak alt aramadan anahtar başına yalnızca ilk satırı alır (max=1)
  - tail son N satırı ters sırayla verir

    cevir(kaynak, sutun_bul) → SQL metni
"""
import re
from datetime import datetime, timezone

SIMDI = "2026-10-19 12:00"
KOMUTLAR = ("search", "where", "eval", "stats", "table", "fields", "rename", "sort", "head", "tail",
            "dedup", "top", "rare", "bin", "bucket", "rex", "join")


class SplHatasi(Exception):
    def __init__(self, msg, konum=None):
        super().__init__(msg)
        self.msg = msg
        self.konum = konum


Hata = SplHatasi


def q(ad):
    return "[" + ad.replace("]", "]]") + "]"


def sql_metin(s):
    return "'" + str(s).replace("'", "''") + "'"


def _metin_coz(t):
    return re.sub(r"\\(.)", lambda m: m.group(1), t[1:-1])


# — jetonlayıcılar —
_ARAMA = re.compile(r'\s*(?:(?P<metin>"(?:\\.|[^"\\])*")|(?P<isl>!=|<=|>=|==|=|<|>|\(|\))|(?P<kelime>[^\s=!<>()"]+))')
_IFADE = re.compile(r"""\s*(?:(?P<metin>"(?:\\.|[^"\\])*")|(?P<alan>'[^'\n]+')|(?P<sayi>\d+(?:\.\d+)?(?!\w))
                    |(?P<isl>==|!=|<=|>=|=|<|>|\(|\)|,|\+|-|\*|/|%|\.)|(?P<kelime>[^\W\d]\w*))""", re.X)
_ALANLAR = re.compile(r'\s*(?:(?P<metin>"(?:\\.|[^"\\])*")|(?P<isl>,|=)|(?P<kelime>[^\s,="]+))')
_STATS = re.compile(r'\s*(?:(?P<metin>"(?:\\.|[^"\\])*")|(?P<isl>[(),=])|(?P<kelime>[^\s(),="]+))')


def _jetonla(desen, metin, bas):
    out, i = [], 0
    while i < len(metin):
        if metin[i:].strip() == "":
            break
        m = desen.match(metin, i)
        if not m or m.end() == i:
            raise SplHatasi(f"tanınmayan karakter: {metin[i:].lstrip()[:1]!r}", bas + i)
        tur = next(t for t, v in m.groupdict().items() if v is not None)
        out.append((tur, m.group(tur), bas + m.start(tur)))
        i = m.end()
    return out


class _Akis:
    def __init__(self, jetonlar, son):
        self.j = jetonlar
        self.i = 0
        self.son = son

    def bak(self, k=0):
        n = self.i + k
        return self.j[n] if n < len(self.j) else ("son", "", self.son)

    def bitti(self):
        return self.i >= len(self.j)

    def al(self):
        t = self.bak()
        self.i += 1
        return t

    def isl_mi(self, v, k=0):
        t = self.bak(k)
        return t[0] == "isl" and t[1] == v

    def kelime_mi(self, v, k=0, harf=False):
        t = self.bak(k)
        return t[0] == "kelime" and (t[1].lower() == v.lower() if not harf else t[1] == v)

    def bekle(self, v):
        t = self.bak()
        if t[1] != v:
            raise SplHatasi(f"'{v}' bekleniyordu, '{t[1] or 'komutun sonu'}' geldi", t[2])
        self.i += 1

    def ad(self):
        t = self.bak()
        if t[0] == "metin":
            self.i += 1
            return _metin_coz(t[1])
        if t[0] != "kelime":
            raise SplHatasi(f"bir alan adı bekleniyordu, '{t[1] or 'komutun sonu'}' geldi", t[2])
        self.i += 1
        return t[1]


def _parcala(kaynak, bas, son):
    """| ile ayır (tırnak ve [ ] içi hariç) → [(metin, mutlak konum)]."""
    parcalar, derinlik, tirnak, i, bas_i = [], 0, False, bas, bas
    while i < son:
        c = kaynak[i]
        if tirnak:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                tirnak = False
        elif c == '"':
            tirnak = True
        elif c == "[":
            derinlik += 1
        elif c == "]":
            derinlik -= 1
        elif c == "|" and derinlik == 0:
            parcalar.append((kaynak[bas_i:i], bas_i))
            bas_i = i + 1
        i += 1
    parcalar.append((kaynak[bas_i:son], bas_i))
    return parcalar


class _Cevirici:
    def __init__(self, kaynak, sutun_bul):
        self.kaynak = kaynak
        self.sutun_bul = sutun_bul
        self.ctes = []

    def yeni(self, sql):
        ad = f"a{len(self.ctes) + 1}"
        self.ctes.append((ad, sql))
        self.sutun_bul(self.with_sql(f"SELECT * FROM {ad} LIMIT 0"))    # aşama hemen denetlensin
        return ad

    def with_sql(self, son):
        if not self.ctes:
            return son
        return "WITH " + ",\n     ".join(f"{a} AS ({s})" for a, s in self.ctes) + "\n" + son

    def sutunlar(self, ad):
        return [c for c in self.sutun_bul(self.with_sql(f"SELECT * FROM {ad} LIMIT 0")) if c != "__sira"]

    def secim(self, cols, on_ek=""):
        return ", ".join(on_ek + q(c) for c in cols)

    # — boru hattı —
    def hat(self, bas, son):
        parcalar = _parcala(self.kaynak, bas, son)
        ilk, ilk_konum = parcalar[0]
        komut0 = ilk.strip().split(None, 1)[0].lower() if ilk.strip() else ""
        if komut0 == "search":
            ilk_konum += ilk.index(ilk.strip().split(None, 1)[0]) + len("search")
            ilk = self.kaynak[ilk_konum:ilk_konum + len(ilk) - (ilk_konum - parcalar[0][1])]
        ad = self.temel_arama(ilk, ilk_konum)
        for metin, konum in parcalar[1:]:
            govde = metin.strip()
            if not govde:
                raise SplHatasi("| işaretinden sonra bir komut bekleniyordu", konum)
            komut = govde.split(None, 1)[0]
            k = komut.lower()
            if k not in KOMUTLAR:
                raise SplHatasi(f"bu komut desteklenmiyor: {komut} (desteklenenler: {', '.join(KOMUTLAR)})",
                                konum + metin.index(komut))
            arg_bas = konum + metin.index(komut) + len(komut)
            arg = self.kaynak[arg_bas:konum + len(metin)]
            ad = getattr(self, "k_" + {"bucket": "bin"}.get(k, k))(ad, arg, arg_bas)
        return ad

    # — arama —
    def temel_arama(self, metin, bas):
        jet = _jetonla(_ARAMA, metin, bas)
        tablo, kalan, n = None, [], 0
        while n < len(jet):
            t = jet[n]
            if t[0] == "kelime" and t[1].lower() in ("sourcetype", "index") and n + 2 < len(jet) and jet[n + 1][1] == "=":
                deger = jet[n + 2]
                d = _metin_coz(deger[1]) if deger[0] == "metin" else deger[1]
                if t[1].lower() == "sourcetype":
                    tablo = d
                elif d not in ("ops", "*"):
                    raise SplHatasi(f"böyle bir index yok: {d} (bu tezgahta index=ops)", deger[2])
                n += 3
                continue
            kalan.append(t)
            n += 1
        if not tablo:
            raise SplHatasi("arama sourcetype=<tablo> ile başlamalı (ör. sourcetype=biletler durum=açık)", bas)
        kaynak = self.yeni(f"SELECT *, rowid AS [__sira] FROM {q(tablo)}")
        if not kalan:
            return kaynak
        return self._arama_uygula(kaynak, kalan, bas + len(metin))

    def k_search(self, onceki, arg, bas):
        jet = _jetonla(_ARAMA, arg, bas)
        if not jet:
            raise SplHatasi("search'ten sonra bir arama ifadesi bekleniyordu", bas)
        return self._arama_uygula(onceki, jet, bas + len(arg))

    def _arama_uygula(self, onceki, jet, son):
        a = _Akis(jet, son)
        cols = self.sutunlar(onceki)
        kosul = self._a_ve(a, cols)
        if not a.bitti():
            t = a.bak()
            raise SplHatasi(f"beklenmeyen: '{t[1]}'", t[2])
        return self.yeni(f"SELECT * FROM {onceki} WHERE {kosul}")

    # Splunk'ın search komutunda öncelik: parantez, NOT, OR, AND (SQL'in tersine OR, AND'den sıkı bağlanır)
    def _a_ve(self, a, cols):
        s = self._a_veya(a, cols)
        while not a.bitti() and not a.isl_mi(")"):
            if a.kelime_mi("AND", harf=True):
                a.i += 1
            s = f"({s} AND {self._a_veya(a, cols)})"
        return s

    def _a_veya(self, a, cols):
        s = self._a_degil(a, cols)
        while a.kelime_mi("OR", harf=True):
            a.i += 1
            s = f"({s} OR {self._a_degil(a, cols)})"
        return s

    def _a_degil(self, a, cols):
        if a.kelime_mi("NOT", harf=True):
            a.i += 1
            return f"(NOT {self._a_degil(a, cols)})"
        if a.isl_mi("("):
            a.i += 1
            s = self._a_ve(a, cols)
            a.bekle(")")
            return f"({s})"
        return self._a_terim(a, cols)

    def _a_terim(self, a, cols):
        t = a.al()
        if t[0] == "isl":
            raise SplHatasi(f"beklenmeyen: '{t[1]}'", t[2])
        if t[0] == "kelime" and a.bak()[0] == "isl" and a.bak()[1] in ("=", "!=", "<", ">", "<=", ">=", "=="):
            alan, op = t[1], a.al()[1]
            v = a.al()
            if v[0] not in ("kelime", "metin"):
                raise SplHatasi(f"'{alan}{op}' sonrasında bir değer bekleniyordu", v[2])
            deger = _metin_coz(v[1]) if v[0] == "metin" else v[1]
            if alan not in cols:
                return "0" if op != "!=" else "0"              # alanı olmayan olay eşleşmez
            if op in ("<", ">", "<=", ">="):
                try:
                    float(deger)
                except ValueError:
                    raise SplHatasi(f"{op} ile karşılaştırma için bir sayı bekleniyordu", v[2])
                return f"({q(alan)} {op} {deger})"
            esit = f"spl_wild({q(alan)}, {sql_metin(deger)})" if "*" in deger else f"spl_esit({q(alan)}, {sql_metin(deger)})"
            return f"({q(alan)} IS NOT NULL AND NOT {esit})" if op == "!=" else esit
        # serbest metin: herhangi bir alanda geçiyorsa
        terim = _metin_coz(t[1]) if t[0] == "metin" else t[1].replace("*", "")
        if not terim:
            return "1"
        return "(" + " OR ".join(f"spl_icerir({q(c)}, {sql_metin(terim)})" for c in cols) + ")"

    # — ifadeler (where, eval) —
    def ifade_cevir(self, arg, bas):
        a = _Akis(_jetonla(_IFADE, arg, bas), bas + len(arg))
        return a, self._i_veya(a)

    def _i_veya(self, a):
        s = self._i_ve(a)
        while a.kelime_mi("OR"):
            a.i += 1
            s = f"({s} OR {self._i_ve(a)})"
        return s

    def _i_ve(self, a):
        s = self._i_degil(a)
        while a.kelime_mi("AND"):
            a.i += 1
            s = f"({s} AND {self._i_degil(a)})"
        return s

    def _i_degil(self, a):
        if a.kelime_mi("NOT"):
            a.i += 1
            return f"(NOT {self._i_degil(a)})"
        return self._i_karsilastir(a)

    def _i_karsilastir(self, a):
        s = self._i_topla(a)
        t = a.bak()
        if t[0] == "isl" and t[1] in ("=", "==", "!=", "<", ">", "<=", ">="):
            a.i += 1
            r = self._i_topla(a)
            op = {"=": "=", "==": "=", "!=": "<>"}.get(t[1], t[1])
            return f"({s} {op} {r})"
        return s

    def _i_topla(self, a):
        s = self._i_carp(a)
        while a.isl_mi("+") or a.isl_mi("-") or a.isl_mi("."):
            op = a.al()[1]
            r = self._i_carp(a)
            s = f"({s} || {r})" if op == "." else f"({s} {op} {r})"
        return s

    def _i_carp(self, a):
        s = self._i_tekli(a)
        while a.isl_mi("*") or a.isl_mi("/") or a.isl_mi("%"):
            op = a.al()[1]
            s = f"({s} {op} {self._i_tekli(a)})"
        return s

    def _i_tekli(self, a):
        if a.isl_mi("-"):
            a.i += 1
            return f"(-{self._i_tekli(a)})"
        return self._i_birincil(a)

    def _i_birincil(self, a):
        t = a.bak()
        if t[0] == "sayi":
            a.i += 1
            return t[1]
        if t[0] == "metin":
            a.i += 1
            return sql_metin(_metin_coz(t[1]))
        if t[0] == "alan":
            a.i += 1
            return q(t[1][1:-1])
        if a.isl_mi("("):
            a.i += 1
            s = self._i_veya(a)
            a.bekle(")")
            return f"({s})"
        if t[0] == "kelime":
            if a.isl_mi("(", 1):
                return self._i_fonksiyon(a)
            a.i += 1
            return q(t[1])
        raise SplHatasi(f"beklenmeyen: '{t[1] or 'ifadenin sonu'}'", t[2])

    def _i_fonksiyon(self, a):
        ad_t = a.al()
        ad, konum = ad_t[1], ad_t[2]
        a.bekle("(")
        args = []
        if not a.isl_mi(")"):
            args.append(self._i_veya(a))
            while a.isl_mi(","):
                a.i += 1
                args.append(self._i_veya(a))
        a.bekle(")")

        def say(*n):
            if len(args) not in n:
                raise SplHatasi(f"{ad}() fonksiyonuna yanlış sayıda argüman verildi", konum)

        f = ad.lower()
        sabit = {"true": "1", "false": "0", "null": "NULL", "now": str(_epoch(SIMDI))}
        if f in sabit:
            say(0)
            return sabit[f]
        tek = {"isnull": "({0} IS NULL)", "isnotnull": "({0} IS NOT NULL)", "len": "length({0})",
               "lower": "spl_kucuk({0})", "upper": "spl_buyuk({0})", "abs": "abs({0})",
               "tonumber": "CAST({0} AS NUMERIC)", "tostring": "CAST({0} AS TEXT)"}
        if f in tek:
            say(1)
            return tek[f].format(args[0])
        if f == "if":
            say(3)
            return f"(CASE WHEN {args[0]} THEN {args[1]} ELSE {args[2]} END)"
        if f == "case":
            if len(args) < 2 or len(args) % 2:
                raise SplHatasi("case(koşul1, değer1, koşul2, değer2, ...) biçiminde çift sayıda argüman bekleniyordu", konum)
            return "(CASE " + " ".join(f"WHEN {args[n]} THEN {args[n + 1]}" for n in range(0, len(args), 2)) + " END)"
        if f == "coalesce":
            return f"coalesce({', '.join(args)}{', NULL' if len(args) == 1 else ''})"
        if f == "round":
            say(1, 2)
            return f"round({', '.join(args)})"
        if f == "substr":
            say(2, 3)
            return f"substr({', '.join(args)})"
        if f == "like":
            say(2)
            return f"spl_like({args[0]}, {args[1]})"
        if f == "match":
            say(2)
            return f"spl_regex({args[0]}, {args[1]})"
        if f == "replace":
            say(3)
            return f"spl_replace({args[0]}, {args[1]}, {args[2]})"
        if f == "strptime":
            say(2)
            return f"spl_strptime({args[0]}, {args[1]})"
        if f == "strftime":
            say(2)
            return f"spl_strftime({args[0]}, {args[1]})"
        if f in ("min", "max"):
            if len(args) < 2:
                raise SplHatasi(f"eval içinde {f}() en az iki değer ister; toplama için stats kullan", konum)
            return f"{f}({', '.join(args)})"
        raise SplHatasi(f"bu fonksiyon desteklenmiyor: {ad}()", konum)

    # — komutlar —
    def k_where(self, onceki, arg, bas):
        a, kosul = self.ifade_cevir(arg, bas)
        if not a.bitti():
            t = a.bak()
            raise SplHatasi(f"beklenmeyen: '{t[1]}'", t[2])
        return self.yeni(f"SELECT * FROM {onceki} WHERE {kosul}")

    def k_eval(self, onceki, arg, bas):
        a = _Akis(_jetonla(_IFADE, arg, bas), bas + len(arg))
        while True:
            t = a.bak()
            if t[0] not in ("kelime", "alan") or not a.isl_mi("=", 1):
                raise SplHatasi("eval alan = ifade biçiminde olmalı", t[2])
            hedef = t[1] if t[0] == "kelime" else t[1][1:-1]
            a.i += 2
            sql = self._i_veya(a)
            cols = self.sutunlar(onceki)
            if hedef in cols:
                secim = ", ".join(f"{sql} AS {q(c)}" if c == hedef else q(c) for c in cols)
            else:
                secim = self.secim(cols) + f", {sql} AS {q(hedef)}"
            onceki = self.yeni(f"SELECT {secim}, [__sira] FROM {onceki}")
            if a.isl_mi(","):
                a.i += 1
                continue
            if not a.bitti():
                t = a.bak()
                raise SplHatasi(f"beklenmeyen: '{t[1]}' (birden çok atamayı virgülle ayır)", t[2])
            return onceki

    def _alan_listesi(self, arg, bas):
        a = _Akis(_jetonla(_ALANLAR, arg, bas), bas + len(arg))
        adlar = []
        while not a.bitti():
            if a.isl_mi(","):
                a.i += 1
                continue
            adlar.append((a.ad(), a.bak(-1)[2]))
        return adlar

    def k_table(self, onceki, arg, bas):
        adlar = self._alan_listesi(arg, bas)
        if not adlar:
            raise SplHatasi("table'dan sonra alan adları bekleniyordu", bas)
        cols = self.sutunlar(onceki)
        secim = ", ".join(q(ad) if ad in cols else f"NULL AS {q(ad)}" for ad, _ in adlar)
        return self.yeni(f"SELECT {secim}, [__sira] FROM {onceki}")

    def k_fields(self, onceki, arg, bas):
        govde = arg.strip()
        cols = self.sutunlar(onceki)
        if govde.startswith("-"):
            at = {ad for ad, _ in self._alan_listesi(arg[arg.index("-") + 1:], bas + arg.index("-") + 1)}
            kalan = [c for c in cols if c not in at]
        else:
            kalan = [ad for ad, _ in self._alan_listesi(arg.replace("+", " ", 1) if govde.startswith("+") else arg, bas)
                     if ad in cols]
        return self.yeni(f"SELECT {self.secim(kalan)}, [__sira] FROM {onceki}")

    def k_rename(self, onceki, arg, bas):
        a = _Akis(_jetonla(_ALANLAR, arg, bas), bas + len(arg))
        cols = self.sutunlar(onceki)
        degis = {}
        while not a.bitti():
            if a.isl_mi(","):
                a.i += 1
                continue
            t = a.bak()
            eski = a.ad()
            if not a.kelime_mi("as"):
                raise SplHatasi("rename eski AS yeni biçiminde olmalı", a.bak()[2])
            a.i += 1
            yeni_ad = a.ad()
            if eski not in cols:
                raise SplHatasi(f"böyle bir alan yok: {eski}", t[2])
            degis[eski] = yeni_ad
        secim = ", ".join(f"{q(c)} AS {q(degis.get(c, c))}" for c in cols)
        return self.yeni(f"SELECT {secim}, [__sira] FROM {onceki}")

    def k_sort(self, onceki, arg, bas):
        jet = _jetonla(_ALANLAR, arg, bas)
        limit, parcalar, yon_bekleyen = None, [], None
        for n, t in enumerate(jet):
            if t[0] == "isl":
                continue
            v = t[1]
            if n == 0 and v.isdigit():
                limit = int(v)
                continue
            if v in ("-", "+"):
                yon_bekleyen = v
                continue
            yon = yon_bekleyen or "+"
            yon_bekleyen = None
            if v[0] in "-+":
                yon, v = v[0], v[1:]
            parcalar.append(f"{q(v)} {'DESC' if yon == '-' else 'ASC'}")
        if not parcalar:
            raise SplHatasi("sort'tan sonra en az bir alan bekleniyordu (azalan için -alan)", bas)
        cols = self.sutunlar(onceki)
        sirali = self.yeni(f"SELECT {self.secim(cols)}, ROW_NUMBER() OVER (ORDER BY {', '.join(parcalar)}, [__sira]) "
                           f"AS [__sira] FROM {onceki}")
        if limit:
            return self.yeni(f"SELECT * FROM {sirali} ORDER BY [__sira] LIMIT {limit}")
        return sirali

    def _sayi_arg(self, arg, bas, varsayilan):
        govde = arg.strip()
        if not govde:
            return varsayilan
        if not govde.isdigit():
            raise SplHatasi("bir sayı bekleniyordu", bas + arg.index(govde))
        return int(govde)

    def k_head(self, onceki, arg, bas):
        return self.yeni(f"SELECT * FROM {onceki} ORDER BY [__sira] LIMIT {self._sayi_arg(arg, bas, 10)}")

    def k_tail(self, onceki, arg, bas):
        n = self._sayi_arg(arg, bas, 10)
        son = self.yeni(f"SELECT * FROM {onceki} ORDER BY [__sira] DESC LIMIT {n}")
        cols = self.sutunlar(son)
        return self.yeni(f"SELECT {self.secim(cols)}, ROW_NUMBER() OVER (ORDER BY [__sira] DESC) AS [__sira] FROM {son}")

    def k_dedup(self, onceki, arg, bas):
        adlar = [ad for ad, _ in self._alan_listesi(arg, bas)]
        if not adlar:
            raise SplHatasi("dedup'tan sonra alan adı bekleniyordu", bas)
        cols = self.sutunlar(onceki)
        anahtar = ", ".join(q(a) for a in adlar)
        return self.yeni(f"SELECT {self.secim(cols)}, [__sira] FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY {anahtar} "
                         f"ORDER BY [__sira]) AS [__ilk] FROM {onceki} WHERE " +
                         " AND ".join(f"{q(a)} IS NOT NULL" for a in adlar) + ") WHERE [__ilk] = 1")

    def k_stats(self, onceki, arg, bas):
        a = _Akis(_jetonla(_STATS, arg, bas), bas + len(arg))
        toplamalar = []
        while not a.bitti() and not a.kelime_mi("by"):
            if a.isl_mi(","):
                a.i += 1
                continue
            t = a.bak()
            if t[0] != "kelime":
                raise SplHatasi(f"bir toplama fonksiyonu bekleniyordu (count, sum, avg...), '{t[1]}' geldi", t[2])
            fn = t[1].lower()
            a.i += 1
            alan = None
            if a.isl_mi("("):
                a.i += 1
                alan = a.ad()
                a.bekle(")")
            sql, varsayilan = self._toplama(fn, alan, t[2])
            ad = varsayilan
            if a.kelime_mi("as"):
                a.i += 1
                ad = a.ad()
            toplamalar.append((ad, sql))
        gruplar = []
        if a.kelime_mi("by"):
            a.i += 1
            while not a.bitti():
                if a.isl_mi(","):
                    a.i += 1
                    continue
                gruplar.append(a.ad())
        if not toplamalar:
            raise SplHatasi("stats'tan sonra en az bir toplama bekleniyordu (ör. stats count by rol)", bas)
        secim = ", ".join([q(g) for g in gruplar] + [f"{s} AS {q(n)}" for n, s in toplamalar])
        if gruplar:
            sira = f"ROW_NUMBER() OVER (ORDER BY {', '.join(q(g) for g in gruplar)})"
            sql = (f"SELECT {secim}, {sira} AS [__sira] FROM {onceki} WHERE "
                   + " AND ".join(f"{q(g)} IS NOT NULL" for g in gruplar)
                   + f" GROUP BY {', '.join(q(g) for g in gruplar)}")
        else:
            sql = f"SELECT {secim}, 1 AS [__sira] FROM {onceki}"
        return self.yeni(sql)

    def _toplama(self, fn, alan, konum):
        if fn == "count":
            return ("COUNT(*)", "count") if alan is None else (f"COUNT({q(alan)})", f"count({alan})")
        if alan is None:
            raise SplHatasi(f"{fn} bir alan ister: {fn}(alan)", konum)
        sablon = {"dc": "COUNT(DISTINCT {0})", "distinct_count": "COUNT(DISTINCT {0})", "sum": "SUM({0})",
                  "avg": "AVG({0})", "mean": "AVG({0})", "min": "MIN({0})", "max": "MAX({0})",
                  "values": "group_concat(DISTINCT {0} ORDER BY {0})", "list": "group_concat({0})"}
        if fn not in sablon:
            raise SplHatasi(f"bu toplama desteklenmiyor: {fn}() (desteklenenler: count, dc, sum, avg, min, max, values, list)", konum)
        return sablon[fn].format(q(alan)), f"{fn}({alan})"

    def _top_rare(self, onceki, arg, bas, azalan):
        a = _Akis(_jetonla(_ALANLAR, arg, bas), bas + len(arg))
        limit, alanlar, gruplar, hedef = 10, [], [], None
        while not a.bitti():
            if a.isl_mi(","):
                a.i += 1
                continue
            t = a.bak()
            if t[0] == "kelime" and t[1].lower() == "limit" and a.isl_mi("=", 1):
                a.i += 2
                limit = int(a.ad())
                continue
            if t[0] == "kelime" and t[1].isdigit() and not alanlar:
                a.i += 1
                limit = int(t[1])
                continue
            if a.kelime_mi("by"):
                a.i += 1
                hedef = gruplar
                continue
            (hedef if hedef is not None else alanlar).append(a.ad())
        if not alanlar:
            raise SplHatasi("top/rare bir alan ister: top rol", bas)
        anahtar = gruplar + alanlar
        sayim = self.yeni(f"SELECT {', '.join(q(c) for c in anahtar)}, COUNT(*) AS [count] FROM {onceki} WHERE "
                          + " AND ".join(f"{q(c)} IS NOT NULL" for c in anahtar)
                          + f" GROUP BY {', '.join(q(c) for c in anahtar)}")
        bolum = f"PARTITION BY {', '.join(q(g) for g in gruplar)} " if gruplar else ""
        yon = "DESC" if azalan else "ASC"
        sirali = self.yeni(
            f"SELECT {', '.join(q(c) for c in anahtar)}, [count], "
            f"printf('%.6f', 100.0 * [count] / SUM([count]) OVER ({bolum.strip()})) AS [percent], "
            f"ROW_NUMBER() OVER ({bolum}ORDER BY [count] {yon}, {', '.join(q(c) for c in alanlar)}) AS [__n] FROM {sayim}")
        sira = ", ".join([q(g) for g in gruplar] + ["[__n]"])
        return self.yeni(f"SELECT {', '.join(q(c) for c in anahtar)}, [count], [percent], "
                         f"ROW_NUMBER() OVER (ORDER BY {sira}) AS [__sira] FROM {sirali} WHERE [__n] <= {limit}")

    def k_top(self, onceki, arg, bas):
        return self._top_rare(onceki, arg, bas, True)

    def k_rare(self, onceki, arg, bas):
        return self._top_rare(onceki, arg, bas, False)

    def k_bin(self, onceki, arg, bas):
        m = re.fullmatch(r"\s*(\S+)\s+span\s*=\s*(\d+)([dhm]?)\s*", arg)
        if not m:
            raise SplHatasi("bin alan span=1d biçiminde olmalı (1d, 1h, 15m ya da bir sayı)", bas)
        alan, n, birim = m.group(1), int(m.group(2)), m.group(3)
        cols = self.sutunlar(onceki)
        if alan not in cols:
            raise SplHatasi(f"böyle bir alan yok: {alan}", bas + arg.index(alan))
        x = q(alan)
        if not birim:
            ifade = f"(CAST({x} / {n} AS INTEGER) * {n})"
        elif birim == "d" and n == 1:
            ifade = f"(date({x}) || ' 00:00')"
        elif birim == "h" and 24 % n == 0:
            ifade = f"(date({x}) || ' ' || printf('%02d:00', (CAST(strftime('%H', {x}) AS INTEGER) / {n}) * {n}))"
        elif birim == "m" and 60 % n == 0:
            ifade = f"(strftime('%Y-%m-%d %H:', {x}) || printf('%02d', (CAST(strftime('%M', {x}) AS INTEGER) / {n}) * {n}))"
        else:
            raise SplHatasi("span için 1d, 24'ü bölen saatler (1h, 6h) ya da 60'ı bölen dakikalar (15m) destekleniyor", bas)
        secim = ", ".join(f"{ifade} AS {q(c)}" if c == alan else q(c) for c in cols)
        return self.yeni(f"SELECT {secim}, [__sira] FROM {onceki}")

    def k_rex(self, onceki, arg, bas):
        m = re.fullmatch(r'\s*field\s*=\s*(\S+)\s+("(?:\\.|[^"\\])*")\s*', arg)
        if not m:
            raise SplHatasi('rex field=alan "(?<ad>desen)" biçiminde olmalı', bas)
        alan, desen = m.group(1), m.group(2)[1:-1].replace('\\"', '"')
        adlar = re.findall(r"\(\?<([A-Za-z_]\w*)>", desen)
        if not adlar:
            raise SplHatasi("rex deseninde en az bir adlı grup olmalı: (?<ad>...)", bas)
        python_deseni = re.sub(r"\(\?<(?=[A-Za-z_])", "(?P<", desen)
        try:
            re.compile(python_deseni)
        except re.error as e:
            raise SplHatasi(f"desen derlenemedi: {e}", bas)
        for ad in adlar:
            cols = self.sutunlar(onceki)
            ifade = f"spl_rex({sql_metin(python_deseni)}, {sql_metin(ad)}, {q(alan)})"
            secim = ", ".join(f"{ifade} AS {q(c)}" if c == ad else q(c) for c in cols)
            if ad not in cols:
                secim += f", {ifade} AS {q(ad)}"
            onceki = self.yeni(f"SELECT {secim}, [__sira] FROM {onceki}")
        return onceki

    def k_join(self, onceki, arg, bas):
        if "[" not in arg or not arg.rstrip().endswith("]"):
            raise SplHatasi("join alan [alt arama] biçiminde olmalı: join sunucu_id [search sourcetype=sunucular ...]", bas)
        ac = arg.index("[")
        kapa = len(arg.rstrip()) - 1
        bas_kisim = arg[:ac]
        secenek = dict(re.findall(r"(\w+)\s*=\s*(\w+)", bas_kisim))
        tur = secenek.get("type", "inner").lower()
        if tur not in ("inner", "left", "outer"):
            raise SplHatasi(f"bu join türü desteklenmiyor: {tur} (inner ya da left)", bas)
        anahtarlar = [k for k in re.split(r"[\s,]+", re.sub(r"\w+\s*=\s*\w+", " ", bas_kisim).strip()) if k]
        if not anahtarlar:
            raise SplHatasi("join için en az bir ortak alan gerekiyor: join sunucu_id [ ... ]", bas)
        alt_bas = bas + ac + 1
        alt_son = bas + kapa
        alt_metin = self.kaynak[alt_bas:alt_son]
        ilk = alt_metin.strip().split(None, 1)
        if ilk and ilk[0].lower() == "search":
            alt_bas += alt_metin.index(ilk[0]) + len("search")
        sag = self.hat(alt_bas, alt_son)
        L, R = self.sutunlar(onceki), self.sutunlar(sag)
        for k in anahtarlar:
            if k not in L or k not in R:
                raise SplHatasi(f"join alanı iki tarafta da olmalı: {k}", bas)
        anahtar = ", ".join(q(k) for k in anahtarlar)
        tek = self.yeni(f"SELECT * FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY {anahtar} ORDER BY [__sira]) AS [__ilk] "
                        f"FROM {sag}) WHERE [__ilk] = 1")
        on = " AND ".join(f"l.{q(k)} = r.{q(k)}" for k in anahtarlar)
        secim = [f"coalesce(r.{q(c)}, l.{q(c)}) AS {q(c)}" if c in R and c not in anahtarlar else f"l.{q(c)} AS {q(c)}"
                 for c in L]
        secim += [f"r.{q(c)} AS {q(c)}" for c in R if c not in L]
        katilim = "JOIN" if tur == "inner" else "LEFT JOIN"
        return self.yeni(f"SELECT {', '.join(secim)}, l.[__sira] AS [__sira] FROM {onceki} AS l {katilim} {tek} AS r ON {on}")


def _epoch(metin):
    return int(datetime.strptime(metin, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc).timestamp())


def cevir(kaynak, sutun_bul):
    if not kaynak.strip():
        raise SplHatasi("arama boş", 0)
    c = _Cevirici(kaynak, sutun_bul)
    ad = c.hat(0, len(kaynak))
    return c.with_sql(f"SELECT * FROM {ad} ORDER BY [__sira]")


def fonksiyonlari_kaydet(db):
    def m(x):
        return "" if x is None else str(x)

    def joker(a, desen):
        if a is None:
            return 0
        rx = "^" + ".*".join(re.escape(p) for p in m(desen).split("*")) + "$"
        return int(re.search(rx, m(a), re.I | re.S) is not None)

    def like(a, desen):
        if a is None:
            return None
        rx = "^" + "".join(".*" if ch == "%" else "." if ch == "_" else re.escape(ch) for ch in m(desen)) + "$"
        return int(re.search(rx, m(a), re.S) is not None)

    def regex(a, desen):
        if a is None:
            return None
        try:
            return int(re.search(m(desen), m(a)) is not None)
        except re.error:
            return 0

    def degistir(a, desen, yeni):
        if a is None:
            return None
        try:
            return re.sub(m(desen), re.sub(r"\\(\d)", r"\\\1", m(yeni)), m(a))
        except re.error:
            return a

    def rex(desen, ad, metin):
        if metin is None:
            return None
        r = re.search(desen, m(metin))
        return r.group(ad) if r else None

    def strptime(metin, bicim):
        if metin is None:
            return None
        try:
            return int(datetime.strptime(m(metin), m(bicim)).replace(tzinfo=timezone.utc).timestamp())
        except ValueError:
            return None

    def strftime(an, bicim):
        if an is None:
            return None
        try:
            return datetime.fromtimestamp(float(an), timezone.utc).strftime(m(bicim))
        except (ValueError, OverflowError, OSError):
            return None

    fonksiyonlar = {
        "spl_esit": (2, lambda a, b: 0 if a is None else int(m(a).lower() == m(b).lower())),
        "spl_wild": (2, joker),
        "spl_icerir": (2, lambda a, b: 0 if a is None else int(m(b).lower() in m(a).lower())),
        "spl_kucuk": (1, lambda a: None if a is None else str(a).lower()),
        "spl_buyuk": (1, lambda a: None if a is None else str(a).upper()),
        "spl_like": (2, like),
        "spl_regex": (2, regex),
        "spl_replace": (3, degistir),
        "spl_rex": (3, rex),
        "spl_strptime": (2, strptime),
        "spl_strftime": (2, strftime),
    }
    for ad, (n, fn) in fonksiyonlar.items():
        db.create_function(ad, n, fn, deterministic=True)
