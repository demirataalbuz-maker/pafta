---
id: jv09
title: Servlet Filtreleri ve Spring Denetleyicileri
summary: Jakarta Servlet (HttpServletRequest, Filter, FilterChain.doFilter) akışı, doFilter öncesi eksik return tuzağı ve Spring (@RestController, @GetMapping, @RequestParam, @PathVariable) anotasyonları.
---

::: anlat Servlet Filtre Zinciri (`Filter` ve `doFilter`)
Java web uygulamalarında (Tomcat, Jetty, Spring Boot) gelen her HTTP isteği denetleyiciye (Controller) ulaşmadan önce bir **Filtre Zincirinden (`FilterChain`)** geçer. Bir filtre kimlik doğrulaması, günlükleme veya başlık kontrolü yapar ve isteğin devam etmesi için **`chain.doFilter(request, response)`** metodunu çağırır:

```java
public void doFilter(HttpServletRequest req, HttpServletResponse res, FilterChain chain)
        throws IOException, ServletException {
    String yol = req.getRequestURI();
    String anahtar = req.getHeader("X-API-Key");

    if (yol.startsWith("/api/ozel/") && !"kilit-42".equals(anahtar)) {
        res.setStatus(401);
        res.getWriter().write("Yetkisiz");
        return;                                    #! KRİTİK: return unutulursa alt satırdaki doFilter yine çalışır!
    }
    chain.doFilter(req, res);                      #! isteği sonraki filtreye veya denetleyiciye devret
}
```

> [!TUZAK] `res.setStatus(401)` veya `res.sendRedirect(...)` sonrasında `return` unutmak!
> Java'da `res.setStatus(401)` veya `res.sendRedirect("/giris")` metottan **çıkarmaz**! Eğer geliştirici hemen altına `return;` yazmayı unutmuşsa, kod akışı devam edip `chain.doFilter(req, res)` satırını çalıştırır ve yetkisiz istek hedef denetleyiciyi gerçekten tetikler!
:::

::: anlat Spring `@RestController` anotasyonlarını okumak
Spring Boot uygulamalarında yönlendirme ve parametre bağlama işini `@` ile başlayan **anotasyonlar (ek açıklamalar)** yapar:

```java
@RestController
@RequestMapping("/api/biletler")                   #! sınıftaki tüm rotaların ortak öneki
public class BiletDenetleyici {

    @GetMapping("/{id}")                           #! GET /api/biletler/42
    public ResponseEntity<String> detay(
            @PathVariable("id") long id,           #! URL yolundaki {id} parçası
            @RequestParam(name = "bicim", defaultValue = "kisa") String bicim, #! ?bicim=... sorgu parametresi
            @RequestHeader(name = "X-Birim", required = false) String birim) { #! HTTP başlığı (opsiyonel)
        return ResponseEntity.ok(id + ":" + bicim + ":" + birim);
    }

    @PostMapping                                   #! POST /api/biletler
    public ResponseEntity<String> olustur(@RequestBody BiletIstegi istek) {
        return ResponseEntity.status(201).body(istek.baslik());
    }
}
```

| Anotasyon | Kaynağı | Varsayılan Zorunluluk |
|---|---|---|
| `@PathVariable` | URL yolu (`/biletler/{id}`) | Zorunlu |
| `@RequestParam` | Sorgu dizgesi (`?sayfa=2`) veya form verisi | `required = true` (`defaultValue` verilirse zorunluluk kalkar) |
| `@RequestHeader` | HTTP başlığı (`X-Birim: finans`) | `required = true` (`required = false` ise yoksa `null` gelir) |
| `@RequestBody` | İstek gövdesi (JSON → Java nesnesi/record) | Zorunlu |

> [!DERİN] `getRequestURI()` ile yönlendirme uyumsuzluğu
> Bir filtre `req.getRequestURI().startsWith("/api/yonetim/")` ile ham URI'yi kontrol ederken, alt katmandaki yönlendirici `//api/yonetim/kullanicilar` veya `/api/acik/../yonetim/kullanicilar` yolunu normalize ederek `/api/yonetim/kullanicilar` denetleyicisine eşleyebilir. Bu yüzden filtrelerde her zaman normalize edilmiş uygulama yolu kontrol edilmelidir.
:::

::: tahmin
Java 21 ile çalıştırıldığında bu filtre simülasyonu ne yazdırır?

```java
import java.util.*;

public class Ornek {
    static List<String> filtreCalistir(String yol, String anahtar, boolean erkenDon) {
        List<String> iz = new ArrayList<>();
        if (yol.startsWith("/yonetim") && !"gizli".equals(anahtar)) {
            iz.add("401:REDDEDILDI");
            if (erkenDon) {
                return iz;
            }
        }
        iz.add("200:DENETLEYICI_CALISTI");
        return iz;
    }

    public static void main(String[] args) {
        System.out.println(filtreCalistir("/yonetim/panel", "yanlis", true));
        System.out.println(filtreCalistir("/yonetim/panel", "yanlis", false));
        System.out.println(filtreCalistir("/acik/liste", null, true));
    }
}
```

```gercek
[401:REDDEDILDI]
[401:REDDEDILDI, 200:DENETLEYICI_CALISTI]
[200:DENETLEYICI_CALISTI]
```

???

`[401:REDDEDILDI]`, `[401:REDDEDILDI, 200:DENETLEYICI_CALISTI]`, `[200:DENETLEYICI_CALISTI]`. İlk çağrıda `erkenDon = true` olduğu için `return` çalışır ve denetleyiciye geçilmez. İkinci çağrıda `return` unutulduğu (`erkenDon = false`) için `401:REDDEDILDI` yazılsa bile akış devam edip `200:DENETLEYICI_CALISTI` adımını da çalıştırır. Üçüncü çağrıda yol `/yonetim` ile başlamadığı için doğrudan denetleyici çalışır.
:::

::: gorev Filtre zinciri simülatörü
Aşağıdaki Java `Filter` metodunun davranışını Python'da `filtre_uygula(metot, ham_yol, basliklar)` fonksiyonu olarak kur ve `(durum_kodu, hedef_calisti_mi, mesaj)` demetini döndür.

```java
public static Sonuc filtreUygula(String metot, String hamYol, Map<String, String> basliklar) {
    String yol = hamYol == null ? "/" : hamYol.trim();
    if ("OPTIONS".equalsIgnoreCase(metot)) {
        return new Sonuc(204, false, "CORS_ONAY");
    }
    if (yol.startsWith("/api/saglik")) {
        return new Sonuc(200, true, "ACIK_UC_NOKTA");
    }
    String anahtar = basliklar == null ? null : basliklar.get("X-API-Key");
    if (anahtar == null || anahtar.trim().length() < 8) {
        return new Sonuc(401, false, "ANAHTAR_YOK_VEYA_KISA");
    }
    if ("POST".equalsIgnoreCase(metot) || "DELETE".equalsIgnoreCase(metot)) {
        String rol = basliklar.getOrDefault("X-Rol", "okuyucu");
        if (!"yazici".equals(rol) && !"yonetici".equals(rol)) {
            return new Sonuc(403, false, "YETKISIZ_METOT");
        }
    }
    return new Sonuc(200, true, "GECIS_ONAYLANDI");
}
```

```starter
def filtre_uygula(metot, ham_yol, basliklar):
    return 200, True, "GECIS_ONAYLANDI"
```

```test
need("filtre_uygula")
eq(filtre_uygula("options", "/api/biletler", None), (204, False, "CORS_ONAY"), "OPTIONS isteği doğrudan 204 dönmeli")
eq(filtre_uygula("GET", "/api/saglik/detay", None), (200, True, "ACIK_UC_NOKTA"), "/api/saglik öneki anahtarsız geçmeli")
eq(filtre_uygula("GET", "/api/biletler", {"X-API-Key": "1234567"}), (401, False, "ANAHTAR_YOK_VEYA_KISA"), "7 karakterli anahtar (< 8) reddedilmeli")
eq(filtre_uygula("GET", "/api/biletler", {"X-API-Key": "12345678"}), (200, True, "GECIS_ONAYLANDI"), "tam 8 karakterli anahtar GET için geçmeli")
eq(filtre_uygula("POST", "/api/biletler", {"X-API-Key": "12345678"}), (403, False, "YETKISIZ_METOT"), "POST isteğinde varsayılan rol okuyucu -> 403")
eq(filtre_uygula("POST", "/api/biletler", {"X-API-Key": "12345678", "X-Rol": "YAZICI"}), (403, False, "YETKISIZ_METOT"), "rol karşılaştırması equals ile büyük-küçük harfe duyarlı!")
eq(filtre_uygula("DELETE", "/api/biletler", {"X-API-Key": "12345678", "X-Rol": "yonetici"}), (200, True, "GECIS_ONAYLANDI"), "yonetici DELETE yapabilmeli")
eq(filtre_uygula("POST", "/api/biletler", {"X-API-Key": "12345678", "X-Rol": "yazici"}), (200, True, "GECIS_ONAYLANDI"), "yazici POST yapabilmeli")
```

```solution
def filtre_uygula(metot, ham_yol, basliklar):
    yol = "/" if ham_yol is None else ham_yol.strip()
    if metot is not None and metot.lower() == "options":
        return 204, False, "CORS_ONAY"
    if yol.startswith("/api/saglik"):
        return 200, True, "ACIK_UC_NOKTA"
    anahtar = None if basliklar is None else basliklar.get("X-API-Key")
    if anahtar is None or len(anahtar.strip()) < 8:
        return 401, False, "ANAHTAR_YOK_VEYA_KISA"
    if metot is not None and metot.upper() in ("POST", "DELETE"):
        rol = basliklar.get("X-Rol", "okuyucu")
        if rol not in ("yazici", "yonetici"):
            return 403, False, "YETKISIZ_METOT"
    return 200, True, "GECIS_ONAYLANDI"
```

```hint
Java kodunda `metot` karşılaştırmaları `.equalsIgnoreCase` ile harf duyarsız, `rol` karşılaştırması ise `.equals` ile harfe duyarlıdır. Anahtar uzunluğu `len(anahtar.strip()) < 8` ile kontrol edilir.
```
:::

::: gorev Spring `@RequestParam` bağlayıcı
Aşağıdaki Spring Boot denetleyici metodunun sorgu parametrelerini (`sorgu_haritasi`) bağlama ve doğrulama davranışını Python'da `bilet_listele_bagla(sorgu_haritasi)` fonksiyonu olarak kur.

```java
@GetMapping("/api/biletler")
public String biletListele(
        @RequestParam(name = "durum", defaultValue = "acik") String durum,
        @RequestParam(name = "sayfa", defaultValue = "1") int sayfa,
        @RequestParam(name = "etiket", required = false) String etiket) {
    if (!List.of("acik", "kapali", "tumu").contains(durum)) {
        return "400:GECERSIZ_DURUM";
    }
    if (sayfa < 1 || sayfa > 50) {
        return "400:GECERSIZ_SAYFA";
    }
    String et = (etiket == null || etiket.isBlank()) ? "YOK" : etiket.trim().toLowerCase();
    return "200:" + durum + ":s=" + sayfa + ":e=" + et;
}
```
*(Not: Spring'de `@RequestParam` bir parametrede metin yoksa veya boş metin `""` verilmişse `defaultValue` değerini kullanır; `sayfa` tam sayıya çevrilemezse `400:TIP_HATASI` döndür.)*

```starter
def bilet_listele_bagla(sorgu_haritasi):
    return "200:acik:s=1:e=YOK"
```

```test
need("bilet_listele_bagla")
eq(bilet_listele_bagla({}), "200:acik:s=1:e=YOK", "tüm varsayılanlarla çağrı")
eq(bilet_listele_bagla({"durum": "", "sayfa": ""}), "200:acik:s=1:e=YOK", "boş metinlerde defaultValue devreye girmeli")
eq(bilet_listele_bagla({"durum": "kapali", "sayfa": "50", "etiket": "  Ag_Sorunu "}),
   "200:kapali:s=50:e=ag_sorunu", "üst sınır sayfa=50 ve etiket normalleştirme")
eq(bilet_listele_bagla({"sayfa": "0"}), "400:GECERSIZ_SAYFA", "sayfa=0 (< 1) reddedilmeli")
eq(bilet_listele_bagla({"sayfa": "51"}), "400:GECERSIZ_SAYFA", "sayfa=51 (> 50) reddedilmeli")
eq(bilet_listele_bagla({"sayfa": "iki"}), "400:TIP_HATASI", "sayı olmayan sayfa -> 400:TIP_HATASI")
eq(bilet_listele_bagla({"durum": "beklemede"}), "400:GECERSIZ_DURUM", "izin listesi dışı durum -> 400:GECERSIZ_DURUM")
```

```solution
import re

def bilet_listele_bagla(sorgu_haritasi):
    sorgu = sorgu_haritasi or {}
    durum = sorgu.get("durum")
    if durum is None or durum == "":
        durum = "acik"
    sayfa_ham = sorgu.get("sayfa")
    if sayfa_ham is None or sayfa_ham == "":
        sayfa_ham = "1"
    if not re.fullmatch(r"[+-]?[0-9]+", str(sayfa_ham).strip()):
        return "400:TIP_HATASI"
    sayfa = int(str(sayfa_ham).strip())
    if durum not in ("acik", "kapali", "tumu"):
        return "400:GECERSIZ_DURUM"
    if sayfa < 1 or sayfa > 50:
        return "400:GECERSIZ_SAYFA"
    etiket = sorgu.get("etiket")
    et = "YOK" if (etiket is None or not etiket.strip()) else etiket.strip().lower()
    return f"200:{durum}:s={sayfa}:e={et}"
```

```hint
Önce `durum` ve `sayfa` için `None` veya `""` ise `defaultValue` ata; `sayfa` tam sayıya çevrilemiyorsa `"400:TIP_HATASI"` döndür. Ardından `durum` izin listesini ve `1 <= sayfa <= 50` sınırlarını kontrol et.
```
:::
