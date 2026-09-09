# CRM Company Stages — Odoo 19.0

**Teknik ad:** `crm_company_stages` · **Lisans:** LGPL-3 · **Modül bedeli:** Ücretsiz

## Ne yapar?
CRM panosundaki aşama sütununa şirket alanı ekler. Aynı satış temsilcisi iki
şirkette çalışabilir; aşamanın şirketi temsilciden bağımsızdır. Müşteri etiketlerini
(`crm.tag`) değiştirmez. Ayrı bir ana menü oluşturmaz; mevcut CRM ekranını genişletir.

## Kullanım
1. Sağ üst şirket seçicisinden çalışılacak şirketi seçin. Tam ayrım için yalnızca o şirket işaretli olsun.
2. CRM fırsat panosunda sütunun çark menüsünden **Düzenle** seçeneğini açın.
3. **Şirket** alanını doldurun; alan boşsa aşama ortaktır.
4. Şirketle uyumlu satış ekibi seçin veya ekip alanını boş bırakın.
5. Yeni fırsat, sürükle-bırak, Kazanıldı ve şirket değiştirme akışlarını test edin.

**İki şirket aynı anda seçiliyse ikisinin aşamaları görünür.** Bu bilinçli,
standart çoklu şirket seçimine uyumlu davranıştır. Ortak aşamalar varsa bunlar
her iki şirkette de görünür; ekip kısıtlamaları yine uygulanır.

## Kurulum
Bu arşivden `crm_company_stages` klasörünü uygun Odoo 19.0 sunucusunun özel
addons dizinine koyun; servisi yeniden başlatın, uygulama listesini güncelleyin.
Gerekirse varsayılan **Uygulamalar** arama filtresini kaldırıp **CRM Company Stages**
arayın. CRM bağımlılığı otomatik kurulur. Odoo.sh veya kendi sunucunuz gerekir;
standart Odoo Online bu Python eklentisini çalıştırmaz.

## Mevcut veriler
Yeni kurulumda mevcut aşamalar otomatik bir şirkete bağlanmaz. Mevcut fırsatlar
silinmez veya taşınmaz. Başka şirketin veya şirketsiz fırsatın kullandığı aşamayı
tek şirkete bağlamak engellenir; arşivli kayıtlar da denetlenir. Önce bu kayıtların
uygun aşamalarını kontrollü biçimde düzenleyin veya aşamayı ortak bırakın.

## Önceki modülden geçiş
Eski teknik adı `ranvals_crm_stage_company` olan modül kuruluysa bu paket doğrudan
kurulamaz. Kurulum koruması iki eklentinin aynı alanı birlikte yönetmesini önler.
**Eski modülü kaldırıp yenisini kurmayın, klasörü yalnızca yeniden adlandırmayın.**
Kurulu bir modülün XML kimlikleri ve alan sahipliği için ayrıca test edilmiş teknik
ad migrasyonu gerekir. Bu dağıtım otomatik veri migrasyonu içermez.

## Kontroller ve sınırlar
Paket statik olarak kontrol edilir. 38 Odoo entegrasyon testi eklenmiştir ancak
bu hazırlık ortamında Odoo/PostgreSQL kurulum testi çalıştırılmamıştır. Üretimden
önce ayrı test veritabanında kurulum, yükseltme ve şirket geçişleri doğrulanmalıdır.
Odoo Enterprise, Studio ve diğer CRM eklentileriyle birleşik test ayrıca gerekir.
Kaldırma şirket ayrımını ortadan kaldırır; kaldırmadan önce yedek alın.

## Ücret ve gizlilik
Modül ücretsizdir. Ücretli ek bağımlılığı, API anahtarı, abonelik, takip kodu veya
uzak lisans kontrolü yoktur. Odoo lisansı ve barındırma giderleri ayrı konudur.
Ürün adı ve tanıtım markasızdır; kaynak atıfları NOTICE dosyasında korunmuştur.
