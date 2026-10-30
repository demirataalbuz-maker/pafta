#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pafta bootstrap — temiz bir klonu çalışır hâle getirir.

Kod git ile gelir; ağır bağımlılıklar (.deps, modeller, docker) git-DIŞIDIR.
Bu betik aşağıda seçilen bileşenleri kurar; bütün derslerin WSL/JDK/.NET/VMware
gereksinimlerini veya SQL/Kusto laboratuvarlarını tek başına tamamlamaz.
İkinci makinede önce README'deki platform gereksinimlerini karşıla:

    git clone https://github.com/demirataalbuz-maker/pafta.git
    cd pafta
    python kur.py            # temel: python/js/powershell bağımlılıkları (.deps)
    python kur.py --senkron  # ilerleme senkronunu (özel gist) bağla

    python kur.py --kontrol  # sadece neyin eksik olduğunu raporla (kurma)
    python kur.py --elastic --splunk --advm   # ağır/isteğe bağlı laboratuvarlar
    python kur.py --ai       # (yakında) Ollama + model + docker (Pafta-AI)
    python kur.py --tam      # temel + burada listelenen ekler; AI yoksa başarısız

İdempotenttir: tekrar çalıştırmak güvenlidir (pip/npm zaten kuruluyu atlar).
İlerleme (hangi dersi bitirdin) koda değil, gist'e gider: bkz. engine/senkron.py.
"""
import argparse
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DEPS = os.path.join(ROOT, ".deps")
PY = sys.executable
sonuclar = []


def kosu(cmd):
    print("  $", " ".join(str(c) for c in cmd))
    try:
        return subprocess.run(cmd, cwd=ROOT).returncode
    except FileNotFoundError as e:
        print("  !", e)
        return 1


def adim(ad, fn, zorunlu=True):
    print(f"\n=== {ad} ===")
    try:
        rc = fn()
    except Exception as e:                 # noqa: BLE001 - bootstrap sürmeli
        print("  ! istisna:", e)
        rc = 1
    sonuclar.append((ad, rc == 0, zorunlu))
    print("  →", "tamam" if rc == 0 else ("HATA" if zorunlu else "atlandı/uyarı"))


def pip_target(req):
    yol = os.path.join(ROOT, req)
    if not os.path.isfile(yol):
        print("  ! yok:", req)
        return 1
    return kosu([PY, "-m", "pip", "install", "--upgrade", "--target", DEPS, "-r", yol])


def ps1(script):
    pw = shutil.which("powershell") or shutil.which("pwsh")
    if not pw:
        print("  ! PowerShell yok")
        return 1
    return kosu([pw, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                 os.path.join(ROOT, script)])


def pyscript(script, *args):
    return kosu([PY, os.path.join(ROOT, script), *args])


def arac(ad):
    return shutil.which(ad) or shutil.which(ad + ".cmd") or shutil.which(ad + ".exe")


def kontrol():
    print("\n=== Durum (kurmadan) ===")
    satir = lambda ad, ok: print(f"  [{'x' if ok else ' '}] {ad}")
    satir(".deps/ (python paket deposu)", os.path.isdir(DEPS))
    satir(".deps/npm (JavaScript)", os.path.isdir(os.path.join(DEPS, "npm")))
    satir(".deps/pwsh (PowerShell 7)", os.path.isdir(os.path.join(DEPS, "pwsh")))
    satir(".deps/sysinternals", os.path.isdir(os.path.join(DEPS, "sysinternals")))
    for a in ("git", "gh", "node", "npm", "docker", "ollama"):
        satir(f"araç: {a}", bool(arac(a)))
    print("\nEksikleri kurmak için: python kur.py  (ağır için --elastic/--splunk/--advm/--ai)")


def main():
    sonuclar.clear()
    ap = argparse.ArgumentParser(description="Pafta bootstrap")
    ap.add_argument("--kontrol", action="store_true", help="sadece raporla")
    ap.add_argument("--senkron", action="store_true", help="ilerleme gist'ini bağla")
    ap.add_argument("--elastic", action="store_true")
    ap.add_argument("--splunk", action="store_true")
    ap.add_argument("--advm", action="store_true")
    ap.add_argument("--ai", action="store_true")
    ap.add_argument("--tam", action="store_true")
    a = ap.parse_args()

    if a.kontrol:
        return kontrol()

    # Connecting progress is not permission to download all lesson runtimes.
    if a.senkron and not any((a.elastic, a.splunk, a.advm, a.ai, a.tam)):
        return kosu([PY, "-m", "engine.senkron", "kur"])

    os.makedirs(DEPS, exist_ok=True)

    # ── temel bağımlılıklar (.deps) ──
    adim("Python: tespit paketleri", lambda: pip_target("requirements-detection.txt"))
    adim("Python: HTTP paketleri", lambda: pip_target("requirements-http.txt"))
    adim("Python: paket/ağ paketleri", lambda: pip_target("requirements-packets.txt"))
    if arac("npm"):
        adim("JavaScript: npm paketleri (.deps/npm)", lambda: pyscript("tools/js_bagimlilik_kur.py"), zorunlu=False)
    else:
        print("\n(npm yok → JavaScript yolu atlandı; Node.js kurulabilir)")
    adim("Sysinternals araçları", lambda: ps1("tools/sysinternals_kur.ps1"), zorunlu=False)
    adim("PowerShell 7 (taşınabilir)", lambda: ps1("tools/pwsh7_kur.ps1"), zorunlu=False)
    adim("Pester (PowerShell test)", lambda: ps1("tools/pester_kur.ps1"), zorunlu=False)

    # ── ağır / isteğe bağlı laboratuvarlar ──
    if a.elastic or a.tam:
        adim("Elastic çalışma zamanı", lambda: pyscript("tools/install_elastic_runtime.py"))
        adim("Elasticsearch ve Kibana", lambda: pyscript("tools/elastic_lab_setup.py", "--pull", "--start"))
    if a.splunk or a.tam:
        def splunk_kur():
            from sandbox.splunk_lab import hazirla
            sorun = hazirla()
            if sorun:
                print("  !", sorun)
                return 1
            return pyscript("tools/splunk_cim_kur.py", "--install")
        adim("Splunk ve mevcut arşivden CIM", splunk_kur)
    if a.advm or a.tam:
        adim("AD laboratuvar VM", lambda: pyscript("tools/setup_ad_vm.py", "--start", "--provision"))

    # ── AI (Pafta-AI) — henüz kurulmadı, yer tutucu ──
    if a.ai or a.tam:
        print("\n=== Pafta-AI (yakında) ===")
        print("  Ollama kurulu mu:", bool(arac("ollama")))
        print("  Docker kurulu mu:", bool(arac("docker")))
        print("  ! Pafta-AI altyapısı (LlmRunner + fixture-replay + model çekme) henüz yok.")
        print("    Kurulunca buraya: ollama pull <ai/modeller.txt> + docker compose up eklenecek.")
        sonuclar.append(("Pafta-AI henüz uygulanmadı", False, True))

    # ── ilerleme senkronu ──
    if a.senkron:
        print("\n=== İlerleme senkronu (gist) ===")
        adim("İlerleme senkronu bağlantısı", lambda: kosu([PY, "-m", "engine.senkron", "kur"]))
        print("  Sonra her oturumda: python -m engine.senkron esitle")

    # ── özet ──
    print("\n================ ÖZET ================")
    hata = 0
    for ad, ok, zorunlu in sonuclar:
        iz = "ok " if ok else ("HATA" if zorunlu else "uyar")
        if not ok and zorunlu:
            hata += 1
        print(f"  [{iz}] {ad}")
    print("\nDoğrulama: python tools/validate.py   (ya da tek yol: ... <yol>)")
    if hata:
        print(f"{hata} zorunlu adım başarısız — yukarıya bak.")
        sys.exit(1)
    if any(not ok for _, ok, _ in sonuclar):
        print("Temel kurulum tamam; yukarıdaki isteğe bağlı eksikler devam ediyor.")
    else:
        print("Seçilen kurulum adımları tamam. Dersleri ayrıca validate ile doğrula.")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
