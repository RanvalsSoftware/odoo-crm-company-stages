# CRM Company Stages — Yayın

Hesap: RanvalsSoftware. Depo: odoo-crm-company-stages.
Ürün adı: CRM Company Stages. Teknik ad: crm_company_stages.
Ücretsiz dağıtım: manifestte fiyat yok, LGPL-3.

## Odoo Apps

Yayıncı hesabıyla https://apps.odoo.com/apps/upload sayfasını açın ve bu Git
deposunu kaydedin. Dalları ayrı kayıt olarak isteyen arayüz için adresler:

```text
https://github.com/RanvalsSoftware/odoo-crm-company-stages.git#17.0
https://github.com/RanvalsSoftware/odoo-crm-company-stages.git#18.0
https://github.com/RanvalsSoftware/odoo-crm-company-stages.git#19.0
```

Dallar taranmalı; tarama ve mağaza onayı GitHub'a yüklemeden ayrıdır. Mağaza
başvurusu henüz otomatik olarak yapılmış sayılmaz. Diğer uygulamaların fiyatı
veya lisansı değiştirilmez.

## Tanıtım sitesi

GitHub Settings > Pages > Deploy from a branch > main > /docs > Save.
Öngörülen adres: https://ranvalssoftware.github.io/odoo-crm-company-stages/
Bu ayar yapılmadan siteyi canlı kabul etmeyin.

## Testler

GitHub Actions içindeki ilk yayın akışı üç sürümün 38'er entegrasyon testini
gerçek Odoo/PostgreSQL konteynerlerinde çalıştırır. Testler geçmeden sürüm
dalları ve indirme ZIPleri yayımlanmaz. Sonraki testler için manuel
Odoo CRM Company Stages checks akışı kullanılabilir.

Eski teknik adı taşıyan kurulu modülün yanına yeni modülü kurmayın. Geçiş için
yedek ve ayrıca test edilmiş teknik-ad migrasyonu gerekir.
