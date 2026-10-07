# Kontrol raporu — Odoo 20.0 — 7 Ekim 2026

**Statik kontrol:** GEÇTİ. **Temiz Odoo/PostgreSQL kurulumu:** GEÇTİ.
**Entegrasyon testleri:** 38 test metodunun tamamı çalıştı ve geçti.
Odoo test özeti 40 test, 0 hata ve 0 başarısızlık bildirdi.

| Denetim | Sonuç |
|---|---|
| Python AST ve derleme | 10 dosya geçti |
| XML ayrıştırma | 2 dosya geçti |
| Odoo 20 birleşik erişim CSV yapısı | Geçti |
| Miras görünüm / XPath | Gerçek Odoo 20 kurulumu geçti |
| Model/form aşama domaini eşleşmesi | 180 kombinasyon geçti |
| Ekip domaini | 12 kombinasyon geçti |
| Şirket erişim domaini | 16 kombinasyon geçti |
| Türkçe PO ve bellekte MO derleme | 11 mesaj geçti |
| Tanıtım HTML dosyası | Script, iframe, form, harici stil veya olay kodu yok |
| Mevcut aşamaları dolduracak company_id alan varsayılanı | Yok |
| Odoo Apps liste fiyatı / currency | 9.99 EUR |
| Ücretli ek modül bağımlılığı | Yok |

Toplam **208 domain kombinasyonu** paket doğrulayıcısında kontrol edilmiştir.

## Üretimden önce

Canlı veritabanını yedekleyin. Enterprise, Studio ve diğer özel CRM
eklentileriyle birlikte kurulum/yükseltme testi yapın. İki şirket, aynı
temsilci, boş sütunlar, ortak aşama, içe aktarma/sürükle-bırak, Kazanıldı,
arşivli kayıt ve şirket değiştirme akışlarını kendi verinizle doğrulayın.
Eski teknik isimden otomatik veri migrasyonu yapılmaz.

Statik kontrolü tekrarlamak için: `python qa/validate_static.py`
Gereksinimler: Python 3, lxml, Babel.
