# 12 · Bats teardown ve ortam farkı

27 Ekim 2026 · Codex

BS30'a bir gerçek Bats yazma görevi eklendi: ilk test dosya üreterek bilerek düşüyor, ikinci test ayrı alanda geçiyor; teardown her iki alanı da siliyor. Testler öğrenci Bats dosyasını ana betikten bağımsız tekrar çalıştırır, iki farklı mutlak yolun sadece çalışma klasöründe oluşturulduğunu, her ikisinin silindiğini ve ilgisiz dokunma/kanit.txt dosyasının korunduğunu ölçer. Sahte kalan=0 raporu yeterli değildir.

Git Bash ile Kali WSL ortam farkları ders içinde belgelendi ve gerçek komutlarla kaydedildi: bu bilgisayarda Git Bash MINGW64, Bash 5.2.37 ve cygpath; Linux kernel release/bats/shellcheck/journalctl yok. Kali Linux, Bash 5.3.9, Bats 1.13.0, ShellCheck 0.11.0 ve journalctl mevcut. Bu envanter makineye özgüdür; bütün Git Bash kurulumlarında araç yoktur diye genellenmedi. WSL backend'inin Windows/Git Bash çağıran kabuktan bağımsız olduğu açıklanıyor.

- Windows ve Git Bash: BS30 1 ders, 11 kontrol TEMİZ; iki ham log eklendi.
- `python -X utf8 tools/test_bash_teardown_environment.py`: 1 gerçek çözüm geçti, 7 yanlış çözüm reddedildi, 0 geçen; ortam ölçümü JSON'da.
- Yeni paket kurulmadı. Dosyalar UTF-8/LF.

Öz değerlendirme: test 24, kapsam 24, derinlik 22, gerçeklik 15, yol 9 = 94/100 (A). Önceki bağımsız 85/100 puan korunur; bağımsız yeniden denetim yapılmadı.
