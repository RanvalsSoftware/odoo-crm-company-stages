# İlk hazırlık raporu (yayın öncesi)

Bu dosya ilk ZIP paketinin hazırlanma anını kaydeder. Güncel kurulum testi sonuçları için GitHub Actions kayıtlarına bakın.

# CRM Company Stages — Yayın hazırlık durumu

9 Eylül 2026.

| Sürüm | Statik kontrol | Domain senaryosu | Eklenen Odoo testi | Çalıştırılan Odoo testi |
|---|---|---:|---:|---:|
| 17.0 | Geçti | 172 | 38 | 0 |
| 18.0 | Geçti | 172 | 38 | 0 |
| 19.0 | Geçti | 208 | 38 | 0 |

Toplam 552 domain kombinasyonu ve 114 entegrasyon test metodu (sürümler arasında
aynı test kapsamının ayrı portları) vardır. Odoo/PostgreSQL ortamı bulunmadığı için
entegrasyon testleri çalıştırılmadı. Gerçek kurulum başarısı veya mağaza onayı iddia edilmez.

Tanıtım sitesi Chromium'da 1440, 768 ve 375 piksel genişlikte kontrol edildi.
A/B/Both seçiminde 3/3/5 temsili sütun doğru gösterildi; sayfa taşması veya JavaScript
hatası görülmedi. Site demosu Odoo'ya bağlanmaz. Görseller gerçek Odoo ekran görüntüsü değildir.

GitHub'daki erişilebilir depolar incelendi; mevcut müşteri depoları değiştirilmedi,
public yapılmadı. Bu teslimde yeni uzak repo oluşturulmadı, GitHub'a commit gönderilmedi,
Odoo Apps ilanı açılmadı ve site internete deploy edilmedi.

Yerel Git bundle içinde main, 17.0, 18.0 ve 19.0 dalları hazırlanmıştır. Yeni ve ayrı
bir depoya aktarılmalıdır. Kimlik bilgisi, müşteri verisi veya sunucu konfigürasyonu yoktur.
