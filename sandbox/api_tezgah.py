# -*- coding: utf-8 -*-
"""Pafta · API tezgahı: oturumlu bir JSON API ve birkaç HTML sayfası.

Dersin hazırlık (`setup`) bloğu bu dosyayı düzenek sürecinde çalıştırır; dosya
127.0.0.1'in boş bir portunda "Pafta Bilet Masası API" uygulamasını başlatır.

Python derslerinde `api` modülü kurulur:

    import api
    api.SUNUCU          # "http://127.0.0.1:PORT"
    api.HOST, api.PORT

Kabuk derslerinde (PowerShell, Bash) hazırlık bloğu adresi çalışma klasöründeki
bir dosyaya yazar; betik onu okur.

Uygulama belirlenimlidir: veri her çalıştırmada sıfırdan kurulur, `Date` başlığı
sabittir (Mon, 19 Oct 2026 09:00:00 GMT), oturum çerezi sabit bir değerdir.

Uçlar
-----
POST /giris                 JSON {"kullanici", "parola"} · doğruysa 200 ve
                            `oturum` çerezi, yanlışsa 401 {"hata": "kimlik"}
GET  /api/biletler?sayfa=N  oturum ister; 401 {"hata": "oturum"}
                            200 {"sayfa", "toplam", "sonraki", "kayitlar": [...]}
                            sayfa 1'den başlar, sayfa başına 3 kayıt;
                            aralık dışı sayfa boş `kayitlar` verir
GET  /api/bilet/<id>        oturum ister; yoksa 404 {"hata": "yok"}
POST /api/bilet             oturum ister; JSON {"baslik", "oncelik"}
                            eksik/boş alan 400 {"hata": "alan"}
                            tanınmayan öncelik 400 {"hata": "oncelik"}
                            aynı başlık zaten varsa 409 {"hata": "yinelenen"}
                            doğruysa 201, Location başlığı ve kaydın kendisi
GET  /durum/<kod>           istenen HTTP durum kodunu döndürür (400-599)
GET  /sayfa/biletler        tablo, bağlantılar ve gizli alanlı form içeren HTML
GET  /sayfa/bozuk           kapanmamış etiketleri olan bozuk HTML
"""
import json
import sys
import threading
import types
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

TARIH = "Mon, 19 Oct 2026 09:00:00 GMT"
OTURUM = "pafta-oturum-2026"
KULLANICI, PAROLA = "analist", "pafta123"
SAYFA_BOYU = 3
ONCELIKLER = ("düşük", "orta", "yüksek")

BILETLER = [
    {"id": 101, "baslik": "web01 disk doldu", "oncelik": "yüksek", "durum": "açık", "sunucu": "web01"},
    {"id": 102, "baslik": "db01 yedek gecikti", "oncelik": "orta", "durum": "açık", "sunucu": "db01"},
    {"id": 103, "baslik": "cache01 yeniden başladı", "oncelik": "düşük", "durum": "çözüldü", "sunucu": "cache01"},
    {"id": 104, "baslik": "web02 sertifika süresi", "oncelik": "yüksek", "durum": "açık", "sunucu": "web02"},
    {"id": 105, "baslik": "db01 yavaş sorgu", "oncelik": "orta", "durum": "çözüldü", "sunucu": "db01"},
    {"id": 106, "baslik": "web03 5xx artışı", "oncelik": "yüksek", "durum": "açık", "sunucu": "web03"},
    {"id": 107, "baslik": "yedek01 disk testi", "oncelik": "düşük", "durum": "açık", "sunucu": "yedek01"},
]

SAYFA_HTML = """<!doctype html>
<html lang="tr">
<head><meta charset="utf-8"><title>Bilet Masası</title></head>
<body>
<h1 id="baslik">Açık Biletler</h1>
<p class="ozet">Toplam <span id="adet">{adet}</span> kayıt listeleniyor.</p>
<table id="biletler">
<thead><tr><th>No</th><th>Başlık</th><th>Öncelik</th><th>Sunucu</th></tr></thead>
<tbody>
{satirlar}
</tbody>
</table>
<ul class="baglantilar">
{baglantilar}
</ul>
<form id="yeni" method="post" action="/api/bilet">
<input type="hidden" name="belirtec" value="form-2026-abc">
<input type="text" name="baslik" value="">
<select name="oncelik"><option value="düşük">düşük</option><option value="orta" selected>orta</option><option value="yüksek">yüksek</option></select>
<button type="submit">Kaydet</button>
</form>
<footer><p class="not">Pafta eğitim verisi</p></footer>
</body>
</html>
"""

BOZUK_HTML = """<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><title>Bozuk Sayfa</title>
<body>
<h1 id="baslik">Yarım Liste
<ul class="kayitlar">
<li class="kayit">web01 <span class="deger">72
<li class="kayit">db01 <span class="deger">91</span>
<li class="kayit">cache01
</ul>
<p class="not">kapanmamış etiketler bilerek bırakıldı
</body>
"""


def _sayfa_html():
    acik = [b for b in BILETLER if b["durum"] == "açık"]
    satirlar = "\n".join(
        '<tr class="bilet" data-id="{id}"><td>{id}</td>'
        '<td><a href="/sayfa/bilet/{id}">{baslik}</a></td>'
        '<td class="oncelik">{oncelik}</td><td>{sunucu}</td></tr>'.format(**b) for b in acik)
    baglantilar = "\n".join(
        '<li><a class="ayrinti" href="/api/bilet/{id}">bilet {id}</a></li>'.format(**b) for b in acik[:3])
    return SAYFA_HTML.format(adet=len(acik), satirlar=satirlar, baglantilar=baglantilar)


class Isleyici(BaseHTTPRequestHandler):
    server_version = "PaftaApi/1.0"
    sys_version = ""
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def date_time_string(self, timestamp=None):
        return TARIH          # send_response'un kendi Date başlığı da sabit olsun

    # ── yardımcılar ──
    def _yolla(self, kod, govde, ctype="application/json; charset=utf-8", ek=()):
        if isinstance(govde, (dict, list)):
            govde = json.dumps(govde, ensure_ascii=False)
        if isinstance(govde, str):
            govde = govde.encode("utf-8")
        self.send_response(kod)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(govde)))
        for ad, deger in ek:
            self.send_header(ad, deger)
        self.end_headers()
        self.wfile.write(govde)

    def _oturum_var(self):
        cerez = self.headers.get("Cookie") or ""
        return f"oturum={OTURUM}" in cerez.replace("; ", ";").replace(";", "; ")

    def _govde_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0 or n > 100_000:
            return None
        try:
            return json.loads(self.rfile.read(n).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None

    def _durum_ucu(self, yol):
        try:
            kod = int(yol.rsplit("/", 1)[1])
        except ValueError:
            return self._yolla(400, {"hata": "kod"})
        if not 400 <= kod <= 599:
            return self._yolla(400, {"hata": "kod"})
        return self._yolla(kod, {"hata": "istek", "kod": kod})

    # ── GET ──
    def do_GET(self):
        u = urlparse(self.path)
        yol = u.path
        if yol == "/sayfa/biletler":
            return self._yolla(200, _sayfa_html(), "text/html; charset=utf-8")
        if yol == "/sayfa/bozuk":
            return self._yolla(200, BOZUK_HTML, "text/html; charset=utf-8")
        if yol.startswith("/durum/"):
            return self._durum_ucu(yol)
        if yol == "/api/biletler":
            if not self._oturum_var():
                return self._yolla(401, {"hata": "oturum"})
            try:
                sayfa = int((parse_qs(u.query).get("sayfa") or ["1"])[0])
            except ValueError:
                return self._yolla(400, {"hata": "sayfa"})
            if sayfa < 1:
                return self._yolla(400, {"hata": "sayfa"})
            bas = (sayfa - 1) * SAYFA_BOYU
            dilim = BILETLER[bas:bas + SAYFA_BOYU]
            sonraki = sayfa + 1 if bas + SAYFA_BOYU < len(BILETLER) else None
            return self._yolla(200, {"sayfa": sayfa, "toplam": len(BILETLER),
                                     "sonraki": sonraki, "kayitlar": dilim})
        if yol.startswith("/api/bilet/"):
            if not self._oturum_var():
                return self._yolla(401, {"hata": "oturum"})
            try:
                no = int(yol.rsplit("/", 1)[1])
            except ValueError:
                return self._yolla(404, {"hata": "yok"})
            kayit = next((b for b in BILETLER if b["id"] == no), None)
            return self._yolla(200, kayit) if kayit else self._yolla(404, {"hata": "yok"})
        return self._yolla(404, {"hata": "yok"})

    # ── POST ──
    def do_POST(self):
        yol = urlparse(self.path).path
        if yol == "/giris":
            veri = self._govde_json() or {}
            if veri.get("kullanici") == KULLANICI and veri.get("parola") == PAROLA:
                cerez = f"oturum={OTURUM}; Path=/; HttpOnly"
                return self._yolla(200, {"durum": "açık", "kullanici": KULLANICI},
                                   ek=[("Set-Cookie", cerez)])
            return self._yolla(401, {"hata": "kimlik"})
        if yol == "/api/bilet":
            if not self._oturum_var():
                return self._yolla(401, {"hata": "oturum"})
            veri = self._govde_json()
            if not isinstance(veri, dict):
                return self._yolla(400, {"hata": "govde"})
            baslik = (veri.get("baslik") or "").strip()
            oncelik = (veri.get("oncelik") or "").strip()
            if not baslik or not oncelik:
                return self._yolla(400, {"hata": "alan"})
            if oncelik not in ONCELIKLER:
                return self._yolla(400, {"hata": "oncelik"})
            eski = next((b for b in BILETLER if b["baslik"].casefold() == baslik.casefold()), None)
            if eski is not None:
                return self._yolla(409, {"hata": "yinelenen", "id": eski["id"]},
                                   ek=[("Location", f"/api/bilet/{eski['id']}")])
            no = max(b["id"] for b in BILETLER) + 1
            kayit = {"id": no, "baslik": baslik, "oncelik": oncelik, "durum": "açık", "sunucu": "-"}
            BILETLER.append(kayit)
            return self._yolla(201, kayit, ek=[("Location", f"/api/bilet/{no}")])
        return self._yolla(404, {"hata": "yok"})


def _kur():
    sunucu = ThreadingHTTPServer(("127.0.0.1", 0), Isleyici)
    sunucu.daemon_threads = True
    sunucu.handle_error = lambda istek, adres: None     # iş parçacığı hataları öğrenci çıktısına karışmasın
    threading.Thread(target=sunucu.serve_forever, daemon=True).start()
    host, port = sunucu.server_address[:2]

    m = types.ModuleType("api")
    m.__doc__ = __doc__
    m.HOST, m.PORT, m.SUNUCU = host, port, f"http://{host}:{port}"
    m.KULLANICI, m.PAROLA = KULLANICI, PAROLA
    m.SUNUCU_NESNESI = sunucu
    sys.modules["api"] = m
    return m


_kur()
