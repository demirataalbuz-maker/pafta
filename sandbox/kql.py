# -*- coding: utf-8 -*-
"""Pafta · KQL → SQLite çevirici.

Kusto Query Language'in öğretilen alt kümesini SQLite SQL'e çevirir. Her boru (|)
aşaması bir CTE olur. Sıralama aşamasından sonra satır sırası gizli bir __sira
sütunuyla taşınır (düzenek sonuçtan atar). Dizgi işleçleri (contains, has,
startswith, =~) KQL'deki gibi büyük-küçük harfe duyarsız olsun diye Python
fonksiyonları olarak kaydedilir: fonksiyonlari_kaydet(db).

    cevir(kaynak, sutun_bul) → SQL metni
    sutun_bul(sql) → o sorgunun sütun adları (her aşamada sorguyu doğrulamak için)
"""
import re

SIMDI = "2026-10-19 12:00"     # now() ve ago() için sabit "şimdi": sonuçlar her gün aynı kalsın

ISLECLER = ("where", "project", "project-away", "project-rename", "extend", "summarize", "sort",
            "order", "take", "limit", "top", "count", "distinct", "join")


class KqlHatasi(Exception):
    def __init__(self, msg, konum=None):
        super().__init__(msg)
        self.msg = msg
        self.konum = konum


_TOKEN = re.compile(r"""
    (?P<bosluk>\s+|//[^\n]*)
  | (?P<tarih>datetime\s*\(\s*(?P<tarih_ic>[^)]*?)\s*\))
  | (?P<metin>@"[^"\n]*"|@'[^'\n]*'|"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*')
  | (?P<sure>\d+(?:\.\d+)?(?:ms|d|h|m|s)(?!\w))
  | (?P<sayi>\d+(?:\.\d+)?(?!\w))
  | (?P<ad>\$?[^\W\d]\w*(?:-(?:away|rename))?)
  | (?P<isl>==|!=|<=|>=|=~|!~|\.\.|[<>=+\-*/%(),.|!;])
""", re.X)
_TURLER = ("bosluk", "tarih", "metin", "sure", "sayi", "ad", "isl")


def _jetonla(kaynak):
    out, i = [], 0
    while i < len(kaynak):
        m = _TOKEN.match(kaynak, i)
        if not m:
            raise KqlHatasi(f"tanınmayan karakter: {kaynak[i]!r}", i)
        tur = next(t for t in _TURLER if m.group(t) is not None)
        if tur == "tarih":
            out.append(("tarih", m.group("tarih_ic"), i))
        elif tur != "bosluk":
            out.append((tur, m.group(tur), i))
        i = m.end()
    return out


Hata = KqlHatasi


def q(ad):
    return "[" + ad.replace("]", "]]") + "]"


def sql_metin(s):
    return "'" + s.replace("'", "''") + "'"


def _metin_coz(t):
    if t.startswith("@"):
        return t[2:-1]                     # @"..." ham metin: ters eğik çizgiler olduğu gibi kalır (regex için)
    govde = t[1:-1]
    return re.sub(r"\\(.)", lambda m: {"n": "\n", "t": "\t"}.get(m.group(1), m.group(1)), govde)


def _tarih(ic):
    ic = ic.strip().strip("\"'").replace("T", " ").rstrip("Z")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}(?: \d{2}:\d{2}(?::\d{2})?)?", ic):
        raise KqlHatasi(f"tarih biçimi anlaşılmadı: {ic!r} (ör. datetime(2026-10-12) ya da datetime(2026-10-12 08:00))")
    return ic[:16]


def _sure(t):
    m = re.fullmatch(r"(\d+(?:\.\d+)?)(ms|d|h|m|s)", t)
    return float(m.group(1)), m.group(2)


# Toplama fonksiyonlarının varsayılan sütun adları (KQL'deki gibi)
_TOPLAMA_ADI = {"count": "count_", "countif": "countif_", "dcount": "dcount_{}", "sum": "sum_{}", "avg": "avg_{}",
                "min": "min_{}", "max": "max_{}", "make_list": "list_{}", "make_set": "set_{}"}
_DIZGI = {"contains": "kql_contains", "contains_cs": "kql_contains_cs", "has": "kql_has", "has_cs": "kql_has_cs",
          "startswith": "kql_startswith", "startswith_cs": "kql_startswith_cs",
          "endswith": "kql_endswith", "endswith_cs": "kql_endswith_cs"}


class _Cevirici:
    def __init__(self, kaynak, sutun_bul):
        self.kaynak = kaynak
        self.j = _jetonla(kaynak)
        self.i = 0
        self.sutun_bul = sutun_bul
        self.ctes = []

    # — jeton yardımcıları —
    def bak(self, k=0):
        n = self.i + k
        return self.j[n] if n < len(self.j) else ("son", "", len(self.kaynak))

    def isl_mi(self, deger, k=0):
        t = self.bak(k)
        return t[0] == "isl" and t[1] == deger

    def kelime_mi(self, deger, k=0):
        t = self.bak(k)
        return t[0] == "ad" and t[1] == deger

    def bekle(self, deger):
        t = self.bak()
        if t[1] != deger:
            raise KqlHatasi(f"'{deger}' bekleniyordu, '{t[1] or 'sorgunun sonu'}' geldi", t[2])
        self.i += 1

    def ad_al(self):
        t = self.bak()
        if t[0] != "ad":
            raise KqlHatasi(f"bir sütun adı bekleniyordu, '{t[1] or 'sorgunun sonu'}' geldi", t[2])
        self.i += 1
        return t[1]

    def virgul(self):
        if self.isl_mi(","):
            self.i += 1
            return True
        return False

    # — CTE yardımcıları —
    def yeni(self, sql):
        ad = f"a{len(self.ctes) + 1}"
        self.ctes.append((ad, sql))
        self.sutunlar(ad, dogrula=True)          # her aşama hemen denetlensin: hata doğru yerde çıksın
        return ad

    def with_sql(self, son):
        if not self.ctes:
            return son
        return "WITH " + ",\n     ".join(f"{a} AS ({s})" for a, s in self.ctes) + "\n" + son

    def sutunlar(self, ad, dogrula=False):
        cols = self.sutun_bul(self.with_sql(f"SELECT * FROM {ad} LIMIT 0"))
        return cols if dogrula else [c for c in cols if c != "__sira"]

    def secim(self, cols, sira, on_ek=""):
        parca = [on_ek + q(c) for c in cols]
        if sira:
            parca.append(on_ek + "[__sira]")
        return ", ".join(parca)

    # — sorgu —
    def sorgu(self):
        """Kaynak (tablo, print ya da parantezli alt sorgu) ve ardından | işleçleri → (CTE adı, sıralı mı)."""
        t = self.bak()
        if t[0] == "isl" and t[1] == "(":
            self.i += 1
            ad, sira = self.sorgu()
            self.bekle(")")
        elif self.kelime_mi("let"):
            raise KqlHatasi("let ifadeleri bu tezgahta desteklenmiyor", t[2])
        elif self.kelime_mi("print"):
            self.i += 1
            ogeler = self.ogeler(varsayilan="print_{}")
            ad, sira = self.yeni("SELECT " + ", ".join(f"{s} AS {q(a)}" for a, s in ogeler)), False
        elif t[0] == "ad":
            self.i += 1
            ad, sira = self.yeni(f"SELECT * FROM {q(t[1])}"), False
        else:
            raise KqlHatasi("sorgu bir tablo adıyla başlamalı (ör. sunucular | where ...)", t[2])
        while self.isl_mi("|"):
            self.i += 1
            op = self.bak()
            if op[0] != "ad":
                raise KqlHatasi("| işaretinden sonra bir işleç bekleniyordu", op[2])
            if op[1] not in ISLECLER:
                raise KqlHatasi(f"bu işleç desteklenmiyor: {op[1]} (desteklenenler: {', '.join(ISLECLER)})", op[2])
            self.i += 1
            ad, sira = getattr(self, "op_" + op[1].replace("-", "_"))(ad, sira)
        return ad, sira

    def ogeler(self, varsayilan="Column{}", toplama=False):
        """`ad = ifade` ya da `ifade`, virgülle ayrık → [(ad, sql)]."""
        out = []
        while True:
            t = self.bak()
            if t[0] == "ad" and self.isl_mi("=", 1):
                self.i += 2
                out.append((t[1], self.ifade()))
            else:
                bas = self.i
                sql = self.ifade()
                ad = None
                if self.i == bas + 1 and t[0] == "ad":
                    ad = t[1]                                       # tek başına bir sütun
                elif t[0] == "ad" and bas + 1 < len(self.j) and self.j[bas + 1][:2] == ("isl", "("):
                    fn = t[1]
                    arg = self.j[bas + 2] if bas + 2 < len(self.j) else ("son", "", 0)
                    if toplama and fn in _TOPLAMA_ADI:
                        ad = _TOPLAMA_ADI[fn].format(arg[1] if arg[0] == "ad" else "")
                    elif fn == "bin" and arg[0] == "ad":
                        ad = arg[1]
                if ad is None:
                    ad = varsayilan.format(len(out) + (0 if "print" in varsayilan else 1))
                out.append((ad, sql))
            if not self.virgul():
                return out

    # — işleçler —
    def op_where(self, onceki, sira):
        return self.yeni(f"SELECT * FROM {onceki} WHERE {self.ifade()}"), sira

    def op_project(self, onceki, sira):
        ogeler = self.ogeler()
        secim = ", ".join(f"{s} AS {q(a)}" for a, s in ogeler) + (", [__sira]" if sira else "")
        return self.yeni(f"SELECT {secim} FROM {onceki}"), sira

    def op_project_away(self, onceki, sira):
        cols = self.sutunlar(onceki)
        at = []
        while True:
            t = self.bak()
            ad = self.ad_al()
            if ad not in cols:
                raise KqlHatasi(f"böyle bir sütun yok: {ad}", t[2])
            at.append(ad)
            if not self.virgul():
                break
        return self.yeni(f"SELECT {self.secim([c for c in cols if c not in at], sira)} FROM {onceki}"), sira

    def op_project_rename(self, onceki, sira):
        cols = self.sutunlar(onceki)
        ad_degis = {}
        while True:
            yeni_ad = self.ad_al()
            self.bekle("=")
            t = self.bak()
            eski = self.ad_al()
            if eski not in cols:
                raise KqlHatasi(f"böyle bir sütun yok: {eski}", t[2])
            ad_degis[eski] = yeni_ad
            if not self.virgul():
                break
        secim = ", ".join(f"{q(c)} AS {q(ad_degis.get(c, c))}" for c in cols) + (", [__sira]" if sira else "")
        return self.yeni(f"SELECT {secim} FROM {onceki}"), sira

    def op_extend(self, onceki, sira):
        for ad, sql in self.ogeler():
            cols = self.sutunlar(onceki)
            if ad in cols:
                secim = ", ".join(f"{sql} AS {q(c)}" if c == ad else q(c) for c in cols)
            else:
                secim = ", ".join(q(c) for c in cols) + f", {sql} AS {q(ad)}"
            onceki = self.yeni(f"SELECT {secim}{', [__sira]' if sira else ''} FROM {onceki}")
        return onceki, sira

    def op_summarize(self, onceki, sira):
        toplamalar = [] if self.kelime_mi("by") else self.ogeler(toplama=True)
        gruplar = []
        if self.kelime_mi("by"):
            self.i += 1
            gruplar = self.ogeler()
        if not toplamalar and not gruplar:
            raise KqlHatasi("summarize'dan sonra bir toplama (ör. count()) ya da by bekleniyordu", self.bak()[2])
        secim = ", ".join(f"{s} AS {q(a)}" for a, s in gruplar + toplamalar)
        sql = f"SELECT {secim} FROM {onceki}"
        if gruplar:
            sql += " GROUP BY " + ", ".join(str(n + 1) for n in range(len(gruplar)))
        return self.yeni(sql), False

    def _siralama(self):
        parcalar = []
        while True:
            e = self.ifade()
            yon = "DESC"                                   # KQL'de varsayılan yön azalandır
            if self.kelime_mi("asc"):
                yon = "ASC"
                self.i += 1
            elif self.kelime_mi("desc"):
                self.i += 1
            parcalar.append(f"{e} {yon}")
            if not self.virgul():
                return parcalar

    def _sirala(self, onceki, sira, parcalar):
        cols = self.sutunlar(onceki)
        anahtar = ", ".join(parcalar) + (", [__sira]" if sira else "")
        return self.yeni(f"SELECT {', '.join(q(c) for c in cols)}, ROW_NUMBER() OVER (ORDER BY {anahtar}) AS [__sira] "
                         f"FROM {onceki}")

    def op_sort(self, onceki, sira):
        self.bekle("by")
        return self._sirala(onceki, sira, self._siralama()), True

    op_order = op_sort

    def _sayi(self):
        t = self.bak()
        if t[0] != "sayi":
            raise KqlHatasi(f"bir sayı bekleniyordu, '{t[1] or 'sorgunun sonu'}' geldi", t[2])
        self.i += 1
        return int(float(t[1]))

    def op_take(self, onceki, sira):
        n = self._sayi()
        return self.yeni(f"SELECT * FROM {onceki}{' ORDER BY [__sira]' if sira else ''} LIMIT {n}"), sira

    op_limit = op_take

    def op_top(self, onceki, sira):
        n = self._sayi()
        self.bekle("by")
        sirali = self._sirala(onceki, sira, self._siralama())
        return self.yeni(f"SELECT * FROM {sirali} ORDER BY [__sira] LIMIT {n}"), True

    def op_count(self, onceki, sira):
        return self.yeni(f"SELECT COUNT(*) AS [Count] FROM {onceki}"), False

    def op_distinct(self, onceki, sira):
        if self.isl_mi("*"):
            self.i += 1
            cols = self.sutunlar(onceki)
        else:
            cols = []
            while True:
                cols.append(self.ad_al())
                if not self.virgul():
                    break
        return self.yeni(f"SELECT DISTINCT {', '.join(q(c) for c in cols)} FROM {onceki}"), False

    def op_join(self, onceki, sira):
        tur = "innerunique"                               # KQL'in varsayılanı
        if self.kelime_mi("kind"):
            self.i += 1
            self.bekle("=")
            t = self.bak()
            tur = self.ad_al()
            if tur not in ("innerunique", "inner", "leftouter", "rightouter", "fullouter", "leftanti", "leftsemi"):
                raise KqlHatasi(f"bu join türü desteklenmiyor: {tur}", t[2])
        if self.isl_mi("("):
            self.i += 1
            sag, _ = self.sorgu()
            self.bekle(")")
        else:
            sag = self.yeni(f"SELECT * FROM {q(self.ad_al())}")
        self.bekle("on")
        kosullar = []
        while True:
            if self.kelime_mi("$left"):
                self.i += 1
                self.bekle(".")
                a = self.ad_al()
                self.bekle("==")
                if not self.kelime_mi("$right"):
                    raise KqlHatasi("$left.a == $right.b biçimi bekleniyordu", self.bak()[2])
                self.i += 1
                self.bekle(".")
                b = self.ad_al()
            else:
                a = b = self.ad_al()
            kosullar.append((a, b))
            if not self.virgul():
                break
        L, R = self.sutunlar(onceki), self.sutunlar(sag)
        on = " AND ".join(f"l.{q(a)} = r.{q(b)}" for a, b in kosullar)
        if tur in ("leftanti", "leftsemi"):
            var = "NOT EXISTS" if tur == "leftanti" else "EXISTS"
            return self.yeni(f"SELECT {', '.join('l.' + q(c) for c in L)} FROM {onceki} AS l "
                             f"WHERE {var} (SELECT 1 FROM {sag} AS r WHERE {on})"), False
        sol = onceki
        if tur == "innerunique":
            # Sol taraf anahtar başına tek satıra indirilir; KQL'in çoğu kişiyi şaşırtan varsayılanı
            anahtar = ", ".join(q(a) for a, _ in kosullar)
            sol = self.yeni(f"SELECT * FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY {anahtar}"
                            f"{' ORDER BY [__sira]' if sira else ''}) AS [__tek] FROM {onceki}) WHERE [__tek] = 1")
        sag_adlar = []
        for c in R:
            yeni_ad, k = c, 1
            while yeni_ad in L or yeni_ad in sag_adlar:
                yeni_ad, k = f"{c}{k}", k + 1
            sag_adlar.append(yeni_ad)
        katilim = {"inner": "JOIN", "innerunique": "JOIN", "leftouter": "LEFT JOIN",
                   "rightouter": "RIGHT JOIN", "fullouter": "FULL JOIN"}[tur]
        secim = [f"l.{q(c)} AS {q(c)}" for c in L] + [f"r.{q(c)} AS {q(n)}" for c, n in zip(R, sag_adlar)]
        return self.yeni(f"SELECT {', '.join(secim)} FROM {sol} AS l {katilim} {sag} AS r ON {on}"), False

    # — ifadeler —
    def ifade(self):
        s = self.ve()
        while self.kelime_mi("or"):
            self.i += 1
            s = f"({s} OR {self.ve()})"
        return s

    def ve(self):
        s = self.karsilastirma()
        while self.kelime_mi("and"):
            self.i += 1
            s = f"({s} AND {self.karsilastirma()})"
        return s

    def karsilastirma(self):
        s = self.toplama()
        t = self.bak()
        if t[0] == "isl" and t[1] in ("==", "!=", "<", "<=", ">", ">=", "=~", "!~"):
            self.i += 1
            r = self.toplama()
            return {"==": f"({s} = {r})", "!=": f"({s} <> {r})", "=~": f"kql_esit({s}, {r})",
                    "!~": f"(NOT kql_esit({s}, {r}))"}.get(t[1], f"({s} {t[1]} {r})")
        olumsuz = False
        if t[0] == "isl" and t[1] == "!" and self.bak(1)[0] == "ad":
            olumsuz = True
            self.i += 1
            t = self.bak()
        sql = None
        if t[0] == "ad" and t[1] in _DIZGI:
            self.i += 1
            sql = f"{_DIZGI[t[1]]}({s}, {self.toplama()})"
        elif t[0] == "ad" and t[1] == "matches" and self.kelime_mi("regex", 1):
            self.i += 2
            sql = f"kql_regex({s}, {self.toplama()})"
        elif t[0] == "ad" and t[1] in ("in", "in~"):
            self.i += 1
            self.bekle("(")
            liste = [self.ifade()]
            while self.virgul():
                liste.append(self.ifade())
            self.bekle(")")
            if t[1] == "in":
                sql = f"({s} IN ({', '.join(liste)}))"
            else:
                sql = f"(kql_kucuk({s}) IN ({', '.join('kql_kucuk(' + x + ')' for x in liste)}))"
        elif t[0] == "ad" and t[1] == "between":
            self.i += 1
            self.bekle("(")
            a = self.toplama()
            self.bekle("..")
            b = self.toplama()
            self.bekle(")")
            sql = f"({s} BETWEEN {a} AND {b})"
        if sql is None:
            if olumsuz:
                raise KqlHatasi("! işaretinden sonra contains, has, startswith, endswith, in ya da between bekleniyordu", t[2])
            return s
        return f"(NOT {sql})" if olumsuz else sql

    def toplama(self):
        s = self.carpma()
        while self.isl_mi("+") or self.isl_mi("-"):
            op = self.bak()[1]
            self.i += 1
            s = f"({s} {op} {self.carpma()})"
        return s

    def carpma(self):
        s = self.tekli()
        while self.isl_mi("*") or self.isl_mi("/") or self.isl_mi("%"):
            op = self.bak()[1]
            self.i += 1
            s = f"({s} {op} {self.tekli()})"
        return s

    def tekli(self):
        if self.isl_mi("-"):
            self.i += 1
            return f"(-{self.tekli()})"
        return self.birincil()

    def birincil(self):
        t = self.bak()
        if t[0] == "sayi":
            self.i += 1
            return t[1]
        if t[0] == "metin":
            self.i += 1
            return sql_metin(_metin_coz(t[1]))
        if t[0] == "tarih":
            self.i += 1
            try:
                return sql_metin(_tarih(t[1]))
            except KqlHatasi as e:
                raise KqlHatasi(e.msg, t[2])
        if t[0] == "sure":
            raise KqlHatasi("süreler (1d, 1h, 30m) yalnızca bin() ve ago() içinde destekleniyor", t[2])
        if self.isl_mi("("):
            self.i += 1
            s = self.ifade()
            self.bekle(")")
            return f"({s})"
        if t[0] == "ad":
            if t[1] in ("true", "false"):
                self.i += 1
                return "1" if t[1] == "true" else "0"
            if self.isl_mi("(", 1):
                return self.fonksiyon()
            self.i += 1
            return q(t[1])
        raise KqlHatasi(f"beklenmeyen: '{t[1] or 'sorgunun sonu'}'", t[2])

    def fonksiyon(self):
        ad_t = self.bak()
        ad = ad_t[1]
        self.i += 2
        if ad == "bin":
            x = self.ifade()
            self.bekle(",")
            t = self.bak()
            if t[0] == "sure":
                self.i += 1
                sql = self._bin_sure(x, t)
            else:
                n = self.ifade()
                sql = f"(CAST(({x}) / ({n}) AS INTEGER) * ({n}))"
            self.bekle(")")
            return sql
        if ad == "ago":
            t = self.bak()
            if t[0] != "sure":
                raise KqlHatasi("ago() içinde bir süre bekleniyordu (ör. ago(1d), ago(6h))", t[2])
            self.i += 1
            self.bekle(")")
            n, birim = _sure(t[1])
            kelime = {"d": "days", "h": "hours", "m": "minutes", "s": "seconds"}.get(birim)
            if not kelime:
                raise KqlHatasi("ago() için d, h, m ya da s kullan", t[2])
            return f"strftime('%Y-%m-%d %H:%M', '{SIMDI}', '-{n:g} {kelime}')"
        args = []
        if not self.isl_mi(")"):
            args.append(self.ifade())
            while self.virgul():
                args.append(self.ifade())
        self.bekle(")")
        return self._fn(ad, args, ad_t[2])

    def _bin_sure(self, x, t):
        n, birim = _sure(t[1])
        n = int(n)
        if birim == "d" and n == 1:
            return f"(date({x}) || ' 00:00')"
        if birim == "h" and 24 % n == 0:
            return f"(date({x}) || ' ' || printf('%02d:00', (CAST(strftime('%H', {x}) AS INTEGER) / {n}) * {n}))"
        if birim == "m" and 60 % n == 0:
            return f"(strftime('%Y-%m-%d %H:', {x}) || printf('%02d', (CAST(strftime('%M', {x}) AS INTEGER) / {n}) * {n}))"
        raise KqlHatasi("bin() zaman için 1d, 24'ü bölen saatler (1h, 6h) ya da 60'ı bölen dakikalar (15m) destekliyor", t[2])

    def _fn(self, ad, a, konum):
        def say(n):
            if len(a) not in (n if isinstance(n, tuple) else (n,)):
                raise KqlHatasi(f"{ad}() fonksiyonuna yanlış sayıda argüman verildi", konum)

        if ad == "count":
            say((0, 1))
            return "COUNT(*)" if not a else f"COUNT({a[0]})"
        tek = {"countif": "SUM(CASE WHEN {0} THEN 1 ELSE 0 END)", "dcount": "COUNT(DISTINCT {0})",
               "sum": "SUM({0})", "avg": "AVG({0})", "min": "MIN({0})", "max": "MAX({0})",
               "make_list": "json_group_array({0})", "make_set": "json_group_array(DISTINCT {0})",
               "strlen": "length({0})", "tolower": "kql_kucuk({0})", "toupper": "kql_buyuk({0})",
               "isnull": "({0} IS NULL)", "isnotnull": "({0} IS NOT NULL)",
               "isempty": "({0} IS NULL OR {0} = '')", "isnotempty": "({0} IS NOT NULL AND {0} <> '')",
               "tostring": "CAST({0} AS TEXT)", "toint": "CAST({0} AS INTEGER)", "tolong": "CAST({0} AS INTEGER)",
               "todouble": "CAST({0} AS REAL)", "toreal": "CAST({0} AS REAL)", "todatetime": "{0}",
               "hourofday": "CAST(strftime('%H', {0}) AS INTEGER)", "startofday": "(date({0}) || ' 00:00')",
               "abs": "abs({0})", "not": "(NOT {0})"}
        if ad in tek:
            say(1)
            return tek[ad].format(a[0])
        if ad == "now":
            say(0)
            return f"'{SIMDI}'"
        if ad == "round":
            say((1, 2))
            return f"round({', '.join(a)})"
        if ad == "substring":
            say((2, 3))
            return f"substr({a[0]}, ({a[1]}) + 1{', ' + a[2] if len(a) == 3 else ''})"
        if ad == "strcat":
            if not a:
                raise KqlHatasi("strcat() en az bir argüman ister", konum)
            return "(" + " || ".join(f"coalesce({x}, '')" for x in a) + ")"
        if ad == "replace_string":
            say(3)
            return f"replace({a[0]}, {a[1]}, {a[2]})"
        if ad in ("iff", "iif"):
            say(3)
            return f"(CASE WHEN {a[0]} THEN {a[1]} ELSE {a[2]} END)"
        if ad == "case":
            if len(a) < 3 or len(a) % 2 == 0:
                raise KqlHatasi("case(koşul1, değer1, ..., varsayılan) biçiminde tek sayıda argüman bekleniyordu", konum)
            dallar = " ".join(f"WHEN {a[n]} THEN {a[n + 1]}" for n in range(0, len(a) - 1, 2))
            return f"(CASE {dallar} ELSE {a[-1]} END)"
        if ad == "coalesce":
            if len(a) < 2:
                raise KqlHatasi("coalesce() en az iki argüman ister", konum)
            return f"coalesce({', '.join(a)})"
        if ad == "extract":
            say(3)
            return f"kql_extract({a[0]}, {a[1]}, {a[2]})"
        if ad == "datetime_diff":
            say(3)
            birim = a[0].strip("'")
            kat = {"day": 1, "hour": 24, "minute": 1440, "second": 86400}.get(birim)
            if kat is None:
                raise KqlHatasi("datetime_diff birimi 'day', 'hour', 'minute' ya da 'second' olmalı", konum)
            # julianday kayan noktalıdır: 209.9999999 dakika 209'a düşmesin diye önce yuvarla
            return f"CAST(round((julianday({a[1]}) - julianday({a[2]})) * {kat}, 6) AS INTEGER)"
        raise KqlHatasi(f"bu fonksiyon desteklenmiyor: {ad}()", konum)


def cevir(kaynak, sutun_bul):
    c = _Cevirici(kaynak, sutun_bul)
    if not c.j:
        raise KqlHatasi("sorgu boş", 0)
    ad, sira = c.sorgu()
    if c.isl_mi(";"):
        c.i += 1
    if c.i < len(c.j):
        t = c.bak()
        raise KqlHatasi(f"beklenmeyen: '{t[1]}' (iki sorguyu boş bir satırla ayır; işleçlerin önüne | koy)", t[2])
    return c.with_sql(f"SELECT * FROM {ad}" + (" ORDER BY [__sira]" if sira else ""))


def fonksiyonlari_kaydet(db):
    """KQL'in dizgi işleçlerini SQLite'a Python fonksiyonu olarak tanıt (null → boş metin, KQL'deki gibi)."""
    def m(x):
        return "" if x is None else str(x)

    def terim(a, b, bayrak):
        return re.search(r"(?<!\w)" + re.escape(m(b)) + r"(?!\w)", m(a), bayrak) is not None

    def regex(a, desen):
        try:
            return int(re.search(m(desen), m(a)) is not None)
        except re.error:
            return 0

    def cikar(desen, grup, metin):
        try:
            r = re.search(m(desen), m(metin))
        except re.error:
            return None
        if not r:
            return None
        try:
            return r.group(int(grup))
        except (IndexError, ValueError):
            return None

    fonksiyonlar = {
        "kql_contains": (2, lambda a, b: int(m(b).lower() in m(a).lower())),
        "kql_contains_cs": (2, lambda a, b: int(m(b) in m(a))),
        "kql_has": (2, lambda a, b: int(terim(a, b, re.I))),
        "kql_has_cs": (2, lambda a, b: int(terim(a, b, 0))),
        "kql_startswith": (2, lambda a, b: int(m(a).lower().startswith(m(b).lower()))),
        "kql_startswith_cs": (2, lambda a, b: int(m(a).startswith(m(b)))),
        "kql_endswith": (2, lambda a, b: int(m(a).lower().endswith(m(b).lower()))),
        "kql_endswith_cs": (2, lambda a, b: int(m(a).endswith(m(b)))),
        "kql_esit": (2, lambda a, b: int(m(a).lower() == m(b).lower())),
        "kql_kucuk": (1, lambda a: None if a is None else str(a).lower()),
        "kql_buyuk": (1, lambda a: None if a is None else str(a).upper()),
        "kql_regex": (2, regex),
        "kql_extract": (3, cikar),
    }
    for ad, (n, fn) in fonksiyonlar.items():
        db.create_function(ad, n, fn, deterministic=True)
