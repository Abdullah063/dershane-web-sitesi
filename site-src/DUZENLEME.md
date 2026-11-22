# Siteyi düzenleme

Bu yapı mevcut HTML, CSS ve animasyonları korur. WordPress, Node.js veya yeni bir framework kurulumu gerekmez.

## Hangi dosya düzenlenir?

- Adres, telefon, e-posta, WhatsApp ve harita: `site-src/site.json`
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

## Temiz sayfa adresleri

Üretici tüm sayfa bağlantılarını uzantısız dizin adreslerine dönüştürür:

- `9-sinif-egitim-kursu.html` kaynağı → `9-sinif-egitim-kursu/index.html` çıktısı → `/9-sinif-egitim-kursu/`
- `iletisim/index.html` kaynağı → `/iletisim/`
- Ana sayfa → `/`

Kaynak şablon adları aynı kalır. Kaynaklarda mevcut HTML bağlantıları kullanılabilir; üretici sayfa bağlantılarını, görselleri, fontları ve JavaScript varlık yollarını yeni konuma göre hesaplar. CSS ve animasyon ayarları değiştirilmez.

Eski kök `.html` dosyaları yönlendirme sayfalarıdır; silmeyin. Apache ve `mod_rewrite` destekleyen hosting için üretilen `.htaccess` dosyasını da yükleyin. Bu dosya eski `.html` ve açık `index.html` isteklerini 301 ile temiz adreslere yönlendirir. Yerel Python sunucusu `.htaccess` çalıştırmaz; eski kök adreslerdeki HTML/JavaScript yedek yönlendirmesi çalışır. Nginx gibi `.htaccess` okumayan sunucularda 301 kuralları hosting yapılandırmasına ayrıca eklenmelidir. Temiz dizin adresleri için framework gerekmez.

Dosyaları çift tıklamak yerine HTTP önizleme sunucusunu kullanın. Yayına yeni sayfa klasörleri ve `.htaccess` dahil tüm üretilen çıktıları birlikte yükleyin.

Adres dönüşümü regresyon kontrolü:

```sh
python3 scripts/test_clean_urls.py
```

## Performance and accessibility build

- `scripts/optimize_page.py` maps optimized images, adds dimensions and accessible link/image names, and corrects the home page heading outline without changing heading styles.
- CSS cascade order is retained in content-hashed bundles. All scripts (including inline configuration) retain their order and run with defer. Upload `assets/kuantum/generated`; do not edit its generated files.
- Original images are retained. Mapping: `site-src/image-optimizations.json`. To regenerate from originals, run `python3 scripts/optimize_images.py` from the project root (requires cwebp).
- `assets/kuantum/site-quality.css` expands pagination touch targets. The loading overlay no longer blocks the content; page animations remain enabled. `site-quality.js` corrects the dynamically created modal's ARIA role.
- Font Awesome 7.0.1 CSS/fonts are served locally with font-display:swap.
- `site-src/hosting-performance.conf` is included in the generated `.htaccess`. Apache must support mod_deflate, mod_expires/mod_headers. Nginx requires equivalent server configuration. Legacy filenames with literal version query suffixes receive proper MIME types.
- Compressed local preview: `python3 scripts/preview_site.py` at http://127.0.0.1:8081/
- `sitemap.xml` uses canonical URLs; `robots.txt` references it. Production domain: kuantumsayisalakademi.com.
- Local audit summary: `site-src/performance-audit.json`. Initial server had no gzip; final preview uses the compression configured for hosting. This is not a live PageSpeed score. LCP is still above target and needs a production retest.

## Yerel arama motoru optimizasyonu

- Sayfa başlıkları, açıklamalar, sayfa türleri ve indeks ayarları `site-src/seo.json` içindedir. Bu dosya ana sayfa, 9-12. sınıf ve YKS sayfalarına özgün Eskişehir/Odunpazarı odaklı açıklamalar sağlar.
- `aliases` aynı kursun diğer adreslerini ana kurs sayfasının canonical adresine bağlar. Ziyaretçi sayfaları korunur; site içi bağlantılar ana adreslere yönelir.
- Arama, yazar, doğrulanmamış öğretmen profili, kategori arşivleri ve aydınlatma sayfası `noindex, follow` kullanır. Robots.txt bu sayfaların taranmasını engellemez; böylece noindex etiketi okunabilir. Site haritası yalnızca 18 asıl indekslenebilir sayfayı listeler.
- `scripts/local_seo.py`, aynı `site.json` adres/telefon verilerinden LocalBusiness/EducationalOrganization, WebSite, WebPage ve BreadcrumbList JSON-LD verisi üretir. Kurs sayfalarında Course bilgisi de bulunur. Yapısal veri, zengin sonuç veya sıralama garantisi değildir.
- Çalışma saatleri, koordinatlar, yorumlar, puanlar ve Google İşletme Profili URL'si doğrulanmadığı için eklenmedi. Bu bilgiler kurum müdüründen teyit edildikten sonra hem görünen içerikle hem yapısal veriyle tutarlı olarak eklenmelidir.
- Kontrol: `python3 scripts/test_local_seo.py`. Başlık/açıklama özgünlüğü, canonical hedefleri, indeks ayarları, JSON-LD içeriği ve site haritası kontrol edilir.
- Yayın sonrasında Google Search Console alan adı doğrulaması, site haritası gönderimi ve ana/kurs/iletişim sayfalarında URL denetimi yapılmalıdır. Google İşletme Profili kaydı kurum yetkilisiyle oluşturulmalı veya mevcut kayıt doğrulanmalıdır. Gerçek kurum fotoğrafları, güncel program bilgileri ve doğal kullanıcı yorumları zamanla tamamlanmalıdır. Sahte yorum veya sıralama garantisi kullanılmaz.
