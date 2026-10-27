# 69 · 72 · 83 · Codex düzeltmelerinin yeniden ölçülmesi

27 Ekim 2026 · Claude.

Üç maddede bağımsız denetimin tek eksiği test boşluklarıydı (yaşayan mutantlar). Codex 26.10.2026'da kapattı (`eb4d26d`, `e3c804d`, `dbe87c7`), ama maddeler yeniden puanlanmadı ve panelde eski test puanı (19, 21, 18) kaldı. Bu teslim yalnız yeniden ölçer; ders değişmedi.

## Ölçüm

- `tools/validate.py cs13 cs16 js13`: 3 ders, 18 kontrol temiz.
- `docs/denetim/araclar/mutasyon.py . cs13 cs16 js13`: **74 mutant, 1 geçen.** Geçen tek mutant JS13:4 çözümünün 31. satırında (`govde !== undefined` → `===`). Bu satır "DENEME: değiştirme" diye işaretli test düzeneğinin parçası; testler gövde göndermediği için davranışı değiştirmez. Eşdeğer olarak raporlandı.
  - CS13: 48 mutant, 48 yakalandı.
  - CS16: 1 mutant, 1 yakalandı (CIL bayt görevinde mutasyon aracı mutant üretmiyor; denetimde zaten temizdi).
  - JS13: 25 mutant, 24 yakalandı, 1 eşdeğer.
- Çıktı: [a-notu-69-72-83-mutasyon.txt](a-notu-69-72-83-mutasyon.txt).

## Öz değerlendirme

Test puanı 24'e çıkar, diğer ölçütler bağımsız denetimdeki gibi kalır: **69: 91, 72: 91, 83: 91 (A).** Bağımsız denetim değildir.
