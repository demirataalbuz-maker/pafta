# -*- coding: utf-8 -*-
"""Java yolundaki JV13'ün gerçek çıktısını üretir: sürümleri kilitli Spring Data JPA düzeneği.

tracks/java/jpa_lab/ (pom.xml + src/Ana.java): Spring Data JPA 4.1.2, Hibernate 7.4.13.Final,
H2 2.5.252 (bellek içi). JDK 21 gerekir (varsayılan: Android Studio'nun JBR'i; JAVA_HOME ile
değiştirilebilir). Maven 3.9.16 ve Maven deposu %LOCALAPPDATA%\Pafta altında tutulur: Windows
komut satırı, proje yolundaki emojili klasör adlarını Java'ya bozuk iletir, bu yüzden araçlar ve
derleme ASCII bir yolda çalışır. Maven yoksa resmi Apache arşivinden indirilir ve SHA-512 ile
doğrulanır. Her çalıştırma geçici bir klasörde derler; depoya bir şey yazmaz.

    python tools/jpa_lab.py
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB = os.path.join(ROOT, "tracks", "java", "jpa_lab")
ARAC = os.path.join(os.environ["LOCALAPPDATA"], "Pafta")
MAVEN_SURUM = "3.9.16"
MAVEN_SHA512 = None   # .sha512 dosyasından okunur ve karşılaştırılır
MAVEN = os.path.join(ARAC, "maven", f"apache-maven-{MAVEN_SURUM}", "bin", "mvn.cmd")
DEPO = os.path.join(ARAC, "m2")
JAVA_HOME = os.environ.get("JAVA_HOME") or r"C:\Program Files\Android\Android Studio\jbr"


def maven_kur():
    if os.path.isfile(MAVEN):
        return
    temel = f"https://archive.apache.org/dist/maven/maven-3/{MAVEN_SURUM}/binaries/apache-maven-{MAVEN_SURUM}-bin.zip"
    gecici = tempfile.mkdtemp(prefix="pafta_maven_")
    try:
        zip_yol = os.path.join(gecici, "maven.zip")
        urllib.request.urlretrieve(temel, zip_yol)
        beklenen = urllib.request.urlopen(temel + ".sha512").read().decode().split()[0]
        gercek = hashlib.sha512(open(zip_yol, "rb").read()).hexdigest()
        if gercek != beklenen:
            sys.exit(f"Maven arşivinin SHA-512 özeti tutmuyor: {gercek[:16]}…")
        zipfile.ZipFile(zip_yol).extractall(os.path.join(ARAC, "maven"))
    finally:
        shutil.rmtree(gecici, ignore_errors=True)


def calistir():
    maven_kur()
    env = dict(os.environ, JAVA_HOME=JAVA_HOME)
    kok = tempfile.mkdtemp(prefix="pafta_jpa_")
    try:
        shutil.copy(os.path.join(LAB, "pom.xml"), kok)
        shutil.copytree(os.path.join(LAB, "src"), os.path.join(kok, "src"))
        cp_dosya = os.path.join(kok, "cp.txt")
        subprocess.run([MAVEN, "-q", "-B", "-f", os.path.join(kok, "pom.xml"), f"-Dmaven.repo.local={DEPO}",
                        "dependency:build-classpath", f"-Dmdep.outputFile={cp_dosya}"], check=True, env=env)
        cp = open(cp_dosya, encoding="utf-8").read().strip()
        cikis = os.path.join(kok, "out")
        bin_ = os.path.join(JAVA_HOME, "bin")
        subprocess.run([os.path.join(bin_, "javac"), "-encoding", "UTF-8", "-parameters", "-d", cikis, "-cp", cp,
                        os.path.join(kok, "src", "Ana.java")], check=True, env=env)
        r = subprocess.run([os.path.join(bin_, "java"), "-Dfile.encoding=UTF-8", "-Dstdout.encoding=UTF-8",
                            "-cp", cikis + os.pathsep + cp, "pafta.jpa.Ana"],
                           env=env, capture_output=True, text=True, encoding="utf-8")
        sys.stdout.write(r.stdout)
        if r.returncode != 0:
            sys.stderr.write(r.stderr[-3000:])
            sys.exit(r.returncode)
    finally:
        shutil.rmtree(kok, ignore_errors=True)


if __name__ == "__main__":
    calistir()
