# Github_Auto_Deployer

![Kategori](https://img.shields.io/badge/Kategori-Genel-blue?style=for-the-badge)
![Lisans](https://img.shields.io/badge/Lisans-MIT-green?style=for-the-badge)
![Durum](https://img.shields.io/badge/Durum-Aktif-success?style=for-the-badge)

## Proje Hakkinda
**Github_Auto_Deployer**, Yarattığınız projeleri ve çalışmaları otomatik olarak githuba yükleyen bir uygulama

Bu proje modern yazilim gelistirme standartlari ve temiz dosya mimarisiyle yapilandirilmistir.

---

## Teknoloji Yigini & Dosya Yapisi
* **Proje Altyapisi:** `Genel (Standart)`
* **Tespit Edilen Kaynak Uzantilari:** `.exe, .html, .ico, .md, .pkg, .py, .pyc, .pyz, .spec, .toc, .txt, .zip`

---

## Proje Dizin Agaci
```text
[DIR] auto_deployer/
  - .gitignore
  - app_icon.ico
  - github_auto_deployer.py
  - GitHub_Pro_Studio.spec
  - GitHub_Pro_Studio_v1.spec
  - LICENSE
  - README.md
  [DIR] build/
    [DIR] GitHub_Pro_Studio/
      - Analysis-00.toc
      - base_library.zip
      - EXE-00.toc
      - GitHub_Pro_Studio.pkg
      - PKG-00.toc
      - PYZ-00.pyz
      - PYZ-00.toc
      - warn-GitHub_Pro_Studio.txt
      - xref-GitHub_Pro_Studio.html
      [DIR] localpycs/
        - pyimod01_archive.pyc
        - pyimod02_importers.pyc
        - pyimod03_ctypes.pyc
        - pyimod04_pywin32.pyc
        - struct.pyc
    [DIR] GitHub_Pro_Studio_v1/
      - Analysis-00.toc
      - base_library.zip
      - EXE-00.toc
      - GitHub_Pro_Studio_v1.pkg
      - PKG-00.toc
      - PYZ-00.pyz
      - PYZ-00.toc
      - warn-GitHub_Pro_Studio_v1.txt
      - xref-GitHub_Pro_Studio_v1.html
      [DIR] localpycs/
        - pyimod01_archive.pyc
        - pyimod02_importers.pyc
        - pyimod03_ctypes.pyc
        - pyimod04_pywin32.pyc
        - struct.pyc
  [DIR] dist/
    - GitHub_Pro_Studio_v1.exe
```

---

## Kurulum ve Calistirma
Projeyi yerel ortaminiza klonlamak icin:
```bash
git clone https://github.com/BatuhanToruk/Github_Auto_Deployer.git
cd Github_Auto_Deployer
```

---

## Lisans
Bu proje **MIT Lisansi** altinda lisanslanmistir.