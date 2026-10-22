---
id: js09
title: Tarayıcı Kodunu Okumak
summary: DOM seçicileri, olay işleyicileri, fetch ile istek, textContent ile innerHTML farkı, çıktıyı kaçırmak ve URL parametrelerini okumak.
kazanim: JSA 4.6.1, JSA 4.10.1
---

::: anlat Bir sayfanın betiğini okumak
Bir web sayfasının JavaScript'i genellikle üç şey yapar: sayfadaki öğeleri **bulur**, kullanıcının yaptıklarını **dinler** ve sunucuyla **konuşur**. Aşağıdaki kod tarayıcıda çalışır; burada çalıştıramayız ama okuyabiliriz:

```javascript norun
const kutu = document.querySelector("#arama");         // id'si arama olan öğe
const liste = document.querySelector("ul.sonuclar");   // sınıfı sonuclar olan ul

kutu.addEventListener("input", async () => {           // her tuş vuruşunda
  const yanit = await fetch(`/api/ara?q=${encodeURIComponent(kutu.value)}`);
  const veri = await yanit.json();
  liste.replaceChildren(...veri.sonuclar.map(s => {
    const li = document.createElement("li");
    li.textContent = s.baslik;                         // metin olarak yaz
    return li;
  }));
});
```

Okurken sorulacak sorular: Hangi öğe? Hangi olay? Hangi adrese istek gidiyor, hangi veriyle? Gelen yanıt sayfaya **nasıl** yazılıyor?

### textContent ve innerHTML
| Yazım | Ne olur |
|---|---|
| `el.textContent = metin` | metin **düz metin** olarak görünür; içindeki `<b>` ekranda harf harf `<b>` yazar |
| `el.innerHTML = metin` | metin **HTML olarak yorumlanır**; etiketler, öznitelikler, bağlantılar çalışır |

> [!GÜVENLİK]
> Kullanıcıdan ya da sunucudan gelen bir metni `innerHTML`'e vermek, o metnin sayfada kod gibi yorumlanmasına izin vermek demektir. Güvenli kod dışarıdan gelen veriyi `textContent` ile yazar ya da HTML'e koymadan önce **kaçırır**: `<`, `>`, `&`, `"` ve `'` karakterlerini zararsız karşılıklarına çevirir. Kod okurken `innerHTML`, `document.write` ve `eval` gördüğün her yer, verinin nereden geldiğini izlemeye değer.

Kaçırmanın kendisi birkaç satırlık bir fonksiyondur:

```javascript
const kacir = s => s
  .replace(/&/g, "&amp;")              #! önce & (yoksa diğerlerini bozar)
  .replace(/</g, "&lt;")
  .replace(/>/g, "&gt;");
console.log(kacir("2 < 3 & 5 > 4"));
```

### URL'yi okumak
İstek adreslerindeki parametreler `URL` ve `URLSearchParams` ile okunur; hem tarayıcıda hem Node'da vardır:

```javascript
const u = new URL("https://ornek.local/ara?q=disk%20dolu&sayfa=2");
console.log(u.pathname, u.searchParams.get("q"), u.searchParams.get("sayfa"));
```
:::

::: tahmin
Tek satır yazar:

```javascript
const kacir = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
console.log(kacir("<b>Merhaba</b> & hoş geldin"));
```

???

`&lt;b&gt;Merhaba&lt;/b&gt; &amp; hoş geldin`. Önce `&` işaretleri `&amp;` olur, sonra açılı parantezler kaçırılır. Bu metin `innerHTML`'e konsa bile tarayıcı onu kalın yazı olarak değil, harfi harfine metin olarak gösterir.
:::

::: gorev Tam kaçırma
`kacir` fonksiyonunu tamamla: `&`, `<`, `>` ile birlikte çift tırnağı `&quot;`, tek tırnağı `&#39;` yapsın. Betik girdinin her satırını kaçırıp yazdırsın.

```starter
const kacir = s => s.replace(/</g, "&lt;").replace(/>/g, "&gt;");
const satirlar = require("fs").readFileSync(0, "utf8").split("\n");
satirlar.pop();
for (const s of satirlar) console.log(kacir(s));
```

```stdin
<a href="x">bağlantı</a>
Ece'nin & Can'ın notu
```

```test
eq(run('<a href="x">bağlantı</a>\n'), "&lt;a href=&quot;x&quot;&gt;bağlantı&lt;/a&gt;\n", "etiket ve çift tırnak")
eq(run("Ece'nin & Can'ın notu\n"), "Ece&#39;nin &amp; Can&#39;ın notu\n", "tek tırnak ve &")
eq(run("&lt;\n"), "&amp;lt;\n", "zaten kaçırılmış görünen metin yeniden kaçırılır")
```

```solution
const kacir = s => s
  .replace(/&/g, "&amp;")
  .replace(/</g, "&lt;")
  .replace(/>/g, "&gt;")
  .replace(/"/g, "&quot;")
  .replace(/'/g, "&#39;");
const satirlar = require("fs").readFileSync(0, "utf8").split("\n");
satirlar.pop();
for (const s of satirlar) console.log(kacir(s));
```

```hint
Sıra önemli: `&` **ilk** değiştirilmeli; yoksa `&lt;` içindeki `&` yeniden `&amp;` olur.
```
:::

::: gorev Adres parametreleri
Girdinin her satırı bir URL. Her biri için `yol q sayfa` yazdır; `sayfa` parametresi yoksa `1` kullan.

```starter
const satirlar = require("fs").readFileSync(0, "utf8").trim().split("\n");
for (const s of satirlar) console.log(s);
```

```stdin
https://ornek.local/ara?q=disk&sayfa=2
https://ornek.local/liste?q=web
```

```test
eq(run("https://ornek.local/ara?q=disk&sayfa=2\nhttps://ornek.local/liste?q=web\n"), "/ara disk 2\n/liste web 1\n", "iki adres")
eq(run("https://ornek.local/ara?q=disk%20dolu&sayfa=3\n"), "/ara disk dolu 3\n", "kodlanmış boşluk çözülür")
```

```solution
const satirlar = require("fs").readFileSync(0, "utf8").trim().split("\n");
for (const s of satirlar) {
  const u = new URL(s);
  console.log(u.pathname, u.searchParams.get("q"), u.searchParams.get("sayfa") ?? "1");
}
```

```hint
`new URL(s)`; yol `u.pathname`, parametre `u.searchParams.get("q")`. Olmayan parametre `null` döner: `?? "1"`.
```
:::
