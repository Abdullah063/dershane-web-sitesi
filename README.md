# Dershane Tanıtım Sitesi

Statik HTML, CSS ve JavaScript tabanlı tanıtım sitesi. WordPress kurulumu gerekmez.

## Yerel önizleme

```sh
python3 -m http.server 8080 --bind 127.0.0.1
```

Tarayıcıda http://127.0.0.1:8080 adresini açın.

## Başlangıç durumu

- Görseller boyut bilgili yer tutucularla değiştirilmiştir.
- Görsel ölçüleri `gorsel-boyutlari.csv` dosyasındadır.
- Metinler genel eğitim içeriğine uyarlanmıştır; gömülü eski site referansları için ek temizlik gereklidir.
- Mobil uygulama ve yönetim paneli henüz geliştirilmemiştir.
- İlk site ve orijinal görseller üst klasörde ayrı tutulur, bu depoya dahil değildir.
