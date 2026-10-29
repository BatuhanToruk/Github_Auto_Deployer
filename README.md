

# 🚀 GitHub Pro Studio

![Kategori](https://img.shields.io/badge/Kategori-Masaüstü_Uygulaması-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-yellow?style=for-the-badge)
![Framework](https://img.shields.io/badge/UI-CustomTkinter-purple?style=for-the-badge)
![Lisans](https://img.shields.io/badge/Lisans-MIT-green?style=for-the-badge)
![Durum](https://img.shields.io/badge/Durum-Aktif-success?style=for-the-badge)

## 📖 Proje Hakkında
**GitHub Pro Studio**, yazılımcıların ve geliştiricilerin projelerini tek tıkla analiz eden, gereksiz şişirici dosyaları (`Library`, `node_modules`, `__pycache__` vb.) otomatik filtreleyen, 100 MB dosya koruması sağlayan ve **Gemini AI** desteğiyle profesyonel bir dokümantasyon (`README.md`) üreterek GitHub'a kusursuzca yükleyen gelişmiş bir masaüstü kontrol panelidir.

Tamamen bağımsız, karanlık temalı ve modern arayüze sahip bu uygulama sayesinde komut satırıyla uğraşmadan tüm süreçleri otonom olarak yönetebilirsiniz.

---

## ✨ Öne Çıkan Özellikler
* **📁 Akıllı Proje & İsim Yönetimi:** Klasör seçtiğinizde projenizi analiz eder, GitHub'da görünecek ismi bizzat sizin belirlemenizi sağlar ve canlı URL önizlemesi sunar.
* **🛡️ 100 MB Büyük Dosya Koruması:** GitHub'ın dosya boyutu sınırına takılmanızı önlemek için devasa dosyaları (`.fbx`, `.blend`, büyük arşivler vb.) otomatik olarak `.gitignore` dosyasına ekler.
* **✨ Yapay Zeka Destekli Dokümantasyon:** Proje klasörünüzün mimarisini tarar ve Gemini AI ile projenize özel rozetli, kurulum adımlı profesyonel bir `README.md` yazar.
* **💾 Kalıcı Hesap Hafızası:** GitHub Token, Kullanıcı Adı ve Gemini API anahtarınızı sadece ilk seferde ayarlar paneline girersiniz; bilgisayarınızda güvenli bir şekilde saklanır.
* **📚 Geçmiş Takibi:** Daha önce bu panel üzerinden yüklediğiniz tüm projeleri listeleyebilir ve tek tıkla tarayıcıda açabilirsiniz.

---

## 🔑 GitHub Personal Access Token (Token) Nasıl Alınır?
Uygulamanın GitHub hesabınıza otomatik depo (repository) açabilmesi ve dosya yükleyebilmesi için bir **Personal Access Token** gereklidir. Token'ı şu adımlarla kolayca oluşturabilirsiniz:

1. Doğrudan token oluşturma sayfasına gitmek için şu bağlantıyı açın: 👉 **[https://github.com/settings/tokens/new](https://github.com/settings/tokens/new)** *(GitHub hesabınıza giriş yapmış olmanız gerekir)*.
2. **Note** alanına uygulamanın adını yazın (Örn: `GitHub Pro Studio`).
3. **Expiration** (Süre) kısmından token'ın geçerlilik süresini seçin (Süresiz olması için `No expiration` seçebilirsiniz).
4. **Select scopes** listesinden en üstte yer alan **`[x] repo`** (Full control of private repositories) kutucuğunu işaretleyin. (Bu seçenek altındaki tüm yetkileri otomatik seçecektir).
5. Sayfanın en altına inerek yeşil **"Generate token"** butonuna tıklayın.
6. Ekranınızda beliren `ghp_...` ile başlayan gizli anahtarı kopyalayın ve uygulamanın **"Ayarlar & Hafıza"** sekmesine yapıştırın.

---

## 🛠️ Kullanılan Teknolojiler
* **Python** (Temel Programlama Dili)
* **CustomTkinter** (Modern Dark-Mode Arayüz Kütüphanesi)
* **GitPython / Subprocess** (Hatasız Git Otomasyonu)
* **Google GenAI SDK** (Yapay Zeka Destekli İçerik Üretimi)

---

## 📂 Uygulama Arayüz Mimarisi
```text
📁 GitHub_Pro_Studio/
  ├── 📁 dist/                 # Derlenmiş bağımsız .exe programı
  ├── 📄 github_auto_deployer.py # Ana kaynak kod
  ├── 📄 app_icon.ico          # Özel uygulama ve roket simgesi
  └── 📄 README.md             # Proje dokümantasyonu
