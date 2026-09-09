# İlk hazırlık raporu (tarihsel kayıt)

Aşağıdaki rapor ilk hazırlık ortamını anlatır. Daha sonra gerçekleştirilen gerçek Odoo testleri için deponun Actions kayıtlarını ve main/VALIDATION.md dosyasını inceleyin.

# Kontrol raporu — Odoo 17.0 — 9 Eylül 2026

**Statik kontrol:** GEÇTİ. **Gerçek Odoo/PostgreSQL kurulumu:** ÇALIŞTIRILMADI.
**Entegrasyon testleri:** 38 test metodu eklendi; 0 test çalıştırıldı.

| Denetim | Sonuç |
|---|---|
| Python AST ve derleme | 10 dosya geçti |
| XML ayrıştırma | 3 dosya geçti |
| Miras görünüm / XPath | 5 görünüm, 9 seçici; küçük yapısal örnekler üzerinde geçti |
| Model/form aşama domaini eşleşmesi | 144 kombinasyon geçti |
| Ekip domaini | 12 kombinasyon geçti |
| Şirket kayıt kuralı | 16 kombinasyon geçti |
| Sürüme özgü grup genişletme imzası / Domain importu | Geçti |
| Türkçe PO ve bellekte MO derleme | 11 mesaj geçti |
| Tanıtım HTML dosyası | Script, iframe, form, harici stil veya olay kodu yok |
| İkon / kapak / açıklama yolları | Dosyalar mevcut |
| Mevcut aşamaları dolduracak company_id alan varsayılanı | Yok |
| Ücretli modül bağımlılığı / price | Yok |

Toplam **172 domain kombinasyonu** denetlendi. Bu kontroller Odoo ORM'yi veya
PostgreSQL'i çalıştırmaz. XPath örnekleri bir canlı birleşik görünüm değildir.
Tarayıcıda test edilen şey ayrı tanıtım sitesidir; Odoo arayüz testi değildir.

## Üretimden önce
Ayrı Odoo 17.0 test veritabanında kurulum ve 38 entegrasyon testini çalıştırın.
İki şirket, aynı temsilci, boş sütunlar, ortak aşama, import/sürükle-bırak,
Kazanıldı, arşivli kayıt ve şirket değiştirme akışlarını gerçek arayüzde doğrulayın.
Studio/Enterprise ve diğer özel modüllerle birleşik senaryolar ayrıca test edilmelidir.
Eski teknik isimden veri migrasyonu yapılmadı. Kaldırma veya güncelleme testi yapılmadı.

Statik kontrolü tekrarlamak için: `python qa/validate_static.py`
Gereksinimler: Python 3, lxml, Babel. Ayrıntılı makine çıktısı: `qa/static_results.json`.
