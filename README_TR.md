# CRM Company Stages

Odoo 17, 18 ve 19 için ücretsiz ve açık kaynaklı, şirket bazlı CRM aşamaları.
Teknik ad: `crm_company_stages`. Lisans: LGPL-3.0-or-later.

## GitHub yayını tamamlandı

| Odoo | Kurulum dalı | Test sonucu |
|---|---|---|
| 17 | [17.0](https://github.com/RanvalsSoftware/odoo-crm-company-stages/tree/17.0) | 38 entegrasyon testi başarılı |
| 18 | [18.0](https://github.com/RanvalsSoftware/odoo-crm-company-stages/tree/18.0) | 38 entegrasyon testi başarılı |
| 19 | [19.0](https://github.com/RanvalsSoftware/odoo-crm-company-stages/tree/19.0) | 38 entegrasyon testi başarılı |

9 Eylül 2026 tarihinde üç sürüm gerçek Odoo Community/PostgreSQL konteynerlerinde kuruldu ve test edildi. [Başarılı yayın ve test kaydı](https://github.com/RanvalsSoftware/odoo-crm-company-stages/actions/runs/34346220917). Ayrıntılar: [VALIDATION.md](VALIDATION.md). Statik kontrollerde toplam 552 şirket/ekip/domain kombinasyonu değerlendirildi. Bu sonuçlar her Enterprise eklentisi veya müşteri özelleştirmesi için garanti değildir; hedef sistemde yedek ve test kurulumu gereklidir.

`main` yalnızca tanıtım sitesi, indirmeler ve yayın belgeleri içindir. Modülü kurarken Odoo sürümünüze uygun dalı kullanın. Hazır modül ZIP'leri [docs/downloads](docs/downloads) klasöründedir.

## Tanıtım sitesi

Site dosyası [docs/index.html](docs/index.html). GitHub Pages yönetim ayarı bu bağlantı üzerinden değiştirilmedi. Ücretsiz siteyi açmak için **Settings > Pages > Deploy from a branch > main > /docs > Save** seçin.

Tanıtım görselleri temsili çizimlerdir, gerçek Odoo ekran görüntüsü değildir.

## Odoo Apps gönderimi

**GitHub'a yükleme, Odoo Apps ilanı oluşturmaz. Odoo Apps gönderimi bu işlem kapsamında yapılmadı.** Yayıncı hesabında şu depo/dalları kaydedin:

```text
https://github.com/RanvalsSoftware/odoo-crm-company-stages.git#17.0
https://github.com/RanvalsSoftware/odoo-crm-company-stages.git#18.0
https://github.com/RanvalsSoftware/odoo-crm-company-stages.git#19.0
```

Üç manifestte de fiyat alanı yoktur ve tek doğrudan bağımlılık ücretsiz `crm` modülüdür. Diğer ücretli uygulama depolarında değişiklik yapılmadı.

## Mevcut kurulum uyarısı

`ranvals_crm_stage_company` kuruluysa yeni teknik adlı modülü yanına kurmayın ve eskisini yalnızca adını değiştirmek için kaldırmayın. Kurulu modülün teknik adının değiştirilmesi ayrı, yedekli ve test edilmiş bir migrasyon gerektirir.

Bu eklenti CRM etiketlerini değil, CRM aşama sütunlarını ayırır. Şirketi boş aşamalar ortaktır; iki şirket seçilirse her iki şirketin aşamaları birlikte görünür. Ayrı görünüm için tek şirket seçin.
