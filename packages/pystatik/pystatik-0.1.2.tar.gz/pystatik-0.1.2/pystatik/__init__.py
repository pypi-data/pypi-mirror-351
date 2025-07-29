def aritmetik_ortalama(veriler):
    return sum(veriler) / len(veriler)

def medyan(veriler):
    sirali = sorted(veriler)
    n = len(sirali)
    if n % 2 == 1:
        return sirali[n // 2]
    else:
        return (sirali[n // 2 - 1] + sirali[n // 2]) / 2

def tepe_degeri(veriler):
    frekanslar = {}
    for sayi in veriler:
        if sayi in frekanslar:
            frekanslar[sayi] += 1
        else:
            frekanslar[sayi] = 1
    en_cok = max(frekanslar.values())
    modlar = [sayi for sayi, tekrar in frekanslar.items() if tekrar == en_cok]
    return modlar[0]

def standart_sapma(veriler):
    ort = aritmetik_ortalama(veriler)
    kare_farklar = [(x - ort) ** 2 for x in veriler]
    varyans = sum(kare_farklar) / (len(veriler) - 1)
    return varyans ** 0.5
