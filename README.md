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

## Statik site temizliği

- Eski kurumun metin, alan adı ve dosya adları Kuantum markasına uyarlandı.
- WordPress API/oEmbed ve RSS dışa aktarımları kaldırıldı.
- Eski analiz hesabı, form gönderim ve emoji yükleme betikleri kaldırıldı.
- `wp-content` ve `wp-includes` altındaki görünüm, menü ve slider bağımlılıkları korunur; bu klasörler topluca silinmemelidir.
- Kayıt ve iletişim formları bir sunucuya bağlı değildir. `assets/kuantum/static-forms.js` gönderimi engeller ve ziyaretçiye bilgi verir. Gerçek form hizmeti bağlanmadan gönderim açılmamalıdır.
- Eski kurum adını içeren sayfa adresleri sadeleştirildi; site içindeki bağlantılar güncellendi.
- Eksik Elementor 4.3.5 dinamik JavaScript parçaları ve Elementor Pro 3.35.1 galeri dosyası aynı sürümlerden tamamlandı.

## Düzenleme ve kontrol

Ortak menü/alt bölüm ve sayfa içeriklerinin kaynakları `site-src/` altındadır. Düzenleme adımları: [site-src/DUZENLEME.md](site-src/DUZENLEME.md).

```sh
python3 scripts/build_site.py
python3 scripts/check_site.py
```

Mevcut tasarım ve animasyonlar korunur. Kök HTML dosyaları üretilen çıktılardır; kalıcı düzenlemeleri kaynak şablonlarda yapın.
