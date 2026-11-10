# Siteyi düzenleme

Bu yapı mevcut HTML, CSS ve animasyonları korur. WordPress, Node.js veya yeni bir framework kurulumu gerekmez.

## Hangi dosya düzenlenir?

- Üst menü ve ortak header: `site-src/partials/header.html.template`
- Ortak alt bölüm: `site-src/partials/footer.html.template`
- Ana sayfa içeriği: `site-src/pages/index.html.template`
- Diğer sayfalar: `site-src/pages/` altında aynı sayfa yolu + `.template`
- Marka renkleri: `assets/kuantum/brand-theme.css`
- Üst slider ve ders şeridi stilleri: `assets/kuantum/hero.css`
- Üst slider davranışı: `assets/kuantum/hero.js`

`{{include:header}}` ve `{{include:footer}}` ortak parçaları yerleştirir.
`{{root}}` alt klasörlerdeki bağlantıların doğru çalışması için otomatik hesaplanır.
Diğer şablon alanları `site-src/pages.json` içindeki mevcut sayfa durumlarını korur (aktif menü, görsel yükleme önceliği gibi). Bunlar normal metin düzenlemesinde değiştirilmez.

## Değişikliği uygulama

Proje klasöründe:

```sh
python3 scripts/build_site.py
python3 scripts/check_site.py
```

Ana dizindeki ve sayfa klasörlerindeki `.html` dosyaları yayımlanabilir çıktıdır. Kalıcı düzenlemeler için önce `site-src` kaynaklarını değiştirin; çıktı dosyasını doğrudan değiştirmek sonraki üretimde üzerine yazılmasına neden olur.

Yalnızca çıktıların güncel olup olmadığını kontrol etmek için:

```sh
python3 scripts/build_site.py --check
```

Önizleme:

```sh
python3 -m http.server 8080 --bind 127.0.0.1
```

## Bağımlılıklar

- Elementor 4.3.5 dinamik parçaları, aynı sürümün resmî WordPress dağıtımından tamamlandı. Ana `frontend.min.js` dosyasıyla paket sürümü birebir doğrulandı.
- Elementor Pro 3.35.1 galeri parçası, mevcut çalışma zamanı dosyasının istediği tam dosya adıyla kaynak sitenin herkese açık statik kopyasından tamamlandı.
- Bu dosyalar yerelden yüklenir. Eski kurumun API'sine veya sunucusuna çalışma zamanı bağımlılığı eklenmedi.
- Tasarım ve animasyon bağımlılıklarını topluca silmeyin; sürüm yükseltmelerini ayrı bir iş olarak değerlendirin.
- Formlar önceki durumdaki gibi gönderime kapalıdır; bu işlemde yeni bir kayıt sistemi eklenmedi.
