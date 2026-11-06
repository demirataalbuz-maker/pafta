# pu26 · Görünür Sentetik Örnekler

`ornekler.json` **sentetiktir**: elle, gerçek biçimlerine bakılarak yazılmıştır; hiçbir konteynerden gelmez.

- `olaylar` (Görev 1): normalleştirilmiş strace olayları. `cagri` sistem çağrısı, `yol` dosya yolu, `argv` execve için komut dizisi, `bayrak` openat açılış bayrakları (`O_WRONLY` vb.).
- `atomik_yaml` (Görev 2): küçük bir Atomic Red Team tanımı.
- `kural` (Görev 3): örnek bir Sigma benzeri kural.

Setup her Çalıştır/Kontrol Et adımında eksik dosyaları kopyalar; **kalıcılık yoktur**. Son görev bu dosyaları kullanmaz; `pafta-linux-lab` konteynerinde gerçek telemetri üretir.
