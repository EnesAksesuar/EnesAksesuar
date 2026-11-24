# YouTube otomatik yayın kurulumu (~15 dakika, ücretsiz)

YouTube Data API ücretsizdir. Günlük 10.000 birim kota verilir, bir video yüklemesi
1.600 birim harcar — yani günde ~6 yükleme. Bize günde 1 lazım, fazlasıyla yeter.
Kanalına yüklemek için Google denetimi **gerekmez** (denetim sadece ekstra kota için).

## 1. Google Cloud projesi
1. https://console.cloud.google.com → yeni proje oluştur (ad: `waithowreal`)
2. **APIs & Services → Library** → "YouTube Data API v3" → **Enable**

## 2. OAuth istemcisi
1. **APIs & Services → OAuth consent screen**
   - User type: **External**
   - Uygulama adı: `waithowreal yukleyici`, destek e-postası: kendi adresin
   - **Test users** bölümüne YouTube kanalının sahibi Google hesabını ekle
   - Yayına almana gerek yok; "Testing" modunda kalabilir
2. **APIs & Services → Credentials → Create Credentials → OAuth client ID**
   - Application type: **Desktop app**
   - Oluşan **Client ID** ve **Client Secret**'i kopyala

## 3. Yetkiyi bir kez al
Kendi bilgisayarında (tarayıcı açılması gerekiyor):

```bash
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```

```bash
YT_CLIENT_ID=... YT_CLIENT_SECRET=... python3 studio/yayinci/yetki_al.py
```

Tarayıcı açılır, kanalın olan hesapla giriş yaparsın, izin verirsin.
Ekrana bir `YT_REFRESH_TOKEN=...` satırı yazılır.

> Bu üç değer paroladır. Sohbete yapıştırma — doğrudan ortam değişkeni olarak ver
> ya da bana söyle, güvenli saklama yoluna koyayım.

## 4. Yükle

```bash
export YT_CLIENT_ID=... YT_CLIENT_SECRET=... YT_REFRESH_TOKEN=...
```

```bash
python3 studio/yayinci/yukle_youtube.py --kuru
```

```bash
python3 studio/yayinci/yukle_youtube.py
```

Yüklenince `kuruk.json` durumu `yayinlandi` olur ve satır `yayin/KAYIT.csv`'ye yazılır.

## 5. Günlük otomatik
Yetki çalıştığı doğrulandıktan sonra, her gün `kuyruk.json` içindeki saatte
sıradaki videoyu yayınlayan bir zamanlanmış görev kurarım.

---

## Instagram ve TikTok

- **Instagram:** ücretsiz, ama hesabın İşletme/Creator olması, bir Facebook Sayfası'na
  bağlı olması ve `instagram_business_content_publish` izni için uygulama incelemesi
  gerekiyor. İnceleme günler–haftalar sürebiliyor. Onaydan sonra tam otomatik.
- **TikTok:** denetimden geçmemiş uygulamalar **yalnızca gizli** paylaşım yapabiliyor
  (`unaudited_client_can_only_post_to_private_accounts`, 403). Yani otomatik herkese
  açık paylaşım denetim olmadan mümkün değil. Pratik yol: videoyu TikTok taslak
  kutusuna göndermek, sen uygulamada tek dokunuşla yayınlamak.
