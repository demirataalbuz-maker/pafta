from sandbox.ai_gercek_ai_savunma_31 import referans_butce as yardimci
import ai_lab

def butce_uygula(istenen, kalan, tavan):
    if isinstance(istenen, bool) or not isinstance(istenen, int) or istenen < 1:
        raise ValueError("istenen pozitif tamsayı olmalı")
    if isinstance(kalan, bool) or not isinstance(kalan, int) or kalan < 0:
        raise ValueError("kalan negatif olmayan tamsayı olmalı")
    if isinstance(tavan, bool) or not isinstance(tavan, int) or tavan < 1:
        raise ValueError("tavan pozitif tamsayı olmalı")
    if kalan < 1:
        return {"karar": "red", "neden": "bütçe tükendi", "num_predict": 0}
    return yardimci(istenen, kalan, tavan)

if ai_lab.CALISTIR:
    from sandbox import ai_gercek_ai_savunma_31 as deney
    deney.goster(butce_uygula)