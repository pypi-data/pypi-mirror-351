def aritmetik_ortalama(veriler):
    return sum(veriler) / len(veriler)

def medyan(veriler):
    sirali = sorted(veriler)
    n = len(sirali)
    if n % 2 == 1:
        return sirali[n // 2]
    else:
        return (sirali[n // 2 - 1] + sirali[n // 2]) / 2

def tepe_degeri(veriler, coklu=False):
    frekanslar = {}
    for sayi in veriler:
        frekanslar[sayi] = frekanslar.get(sayi, 0) + 1

    en_cok = max(frekanslar.values())
    modlar = [sayi for sayi, tekrar in frekanslar.items() if tekrar == en_cok]

    if coklu:
        return modlar
    else:
        return modlar[0]

def standart_sapma(veriler):
    ort = aritmetik_ortalama(veriler)
    kare_farklar = [(x - ort) ** 2 for x in veriler]
    varyans = sum(kare_farklar) / (len(veriler) - 1)
    return varyans ** 0.5

def hesapla(veri_listesi, bicimli=False):
    """
    Tüm temel istatistikleri döndürür.
    - bicimli=True -> String olarak döner (print için süper)
    - bicimli=False -> Dict olarak döner (varsayılan)
    """
    ort = aritmetik_ortalama(veri_listesi)
    med = medyan(veri_listesi)
    mod = tepe_degeri(veri_listesi)
    std = standart_sapma(veri_listesi)
    if bicimli:
        sonuc = (
            f"Ortalama: {ort:.3f}\n"
            f"Medyan: {med:.3f}\n"
            f"Mod: {mod}\n"
            f"Standart Sapma: {std:.3f}"
        )
        return sonuc
    else:
        return {
            "Ortalama": ort,
            "Medyan": med,
            "Mod": mod,
            "Standart Sapma": std
        }

def renkli_yazdir(veriler):
    try:
        from colorama import Fore, Style, init
    except ImportError:
        import os
        os.system('pip install colorama')
        from colorama import Fore, Style, init

    BOLD = '\033[1m'
    ITALIC = '\033[3m'
    RESET_ALL = Style.RESET_ALL

    init(autoreset=True)

    print(BOLD + Fore.YELLOW + "📊 Ortalama: " + Fore.GREEN + ITALIC + str(aritmetik_ortalama(veriler)) + RESET_ALL)
    print(BOLD + Fore.YELLOW + "📈 Medyan: " + Fore.BLUE + ITALIC + str(medyan(veriler)) + RESET_ALL)
    print(BOLD + Fore.YELLOW + "⭐ Mod: " + Fore.MAGENTA + ITALIC + str(tepe_degeri(veriler)) + RESET_ALL)
    print(BOLD + Fore.YELLOW + "📉 Standart Sapma: " + Fore.RED + ITALIC + str(round(standart_sapma(veriler), 3)) + RESET_ALL)
