
🔥 RenScan Toolkit: Advanced Recon & Scanning Suite 🔥

Selamat datang di RenScan Toolkit, solusi serbaguna untuk pengujian keamanan, pengumpulan informasi, dan eksplorasi target secara mendalam.
Didesain dengan fitur canggih dan fleksibilitas penuh, RenScan memungkinkan Anda melakukan recon, pemindaian XSS, enumerasi subdomain, dan masih banyak lagi.

> maaf jika ada yang error karena saya membuat nya saat malam hari🗿, kalau ingin bertanya tentang script nya atau ada error langsung chat whatsapp saya aja dengan nomor yang sudah saya catat di paling bawah.

🌐 Repositori GitHub: RenScan Toolkit


---

✨ Fitur Utama

✅ Advanced Recon:
Kumpulkan informasi detail tentang target seperti SSL, WHOIS, header HTTP, subdomain, port terbuka, dan teknologi yang digunakan.

✅ XSS Payload Scanner:
Deteksi celah XSS pada URL dengan payload khusus. Dirancang untuk menyerupai alat seperti XSStrike.

✅ Subdomain Enumeration:
Lakukan enumerasi subdomain menggunakan file pendukung.

✅ Port Scanning:
Identifikasi port terbuka pada target untuk analisis lebih dalam.

✅ Integrasi File Eksternal:
Gunakan file eksternal seperti subdomains.txt, directories.txt, dan payloads.py untuk memperluas cakupan pemindaian.


---

📂 Struktur Direktori

Berikut struktur direktori penting dalam toolkit ini:
```
RenScan/
├── scan/                  # Folder untuk menyimpan script utama
│   ├── scan8.py           # Advanced Recon
│   ├── scan7.py           # XSS Payload Scanner
│   ├── cek_header2.py     # Header & Teknologi
│   ├── cookie.py          # Cookie Analysis
│   ├── www.py             # Subdomain Scanner
├── subdomains.txt         # (Opsional) Daftar subdomain
├── directories.txt        # (Opsional) Daftar direktori
├── payloads.py            # (Opsional) Daftar payload untuk XSS
└── main_menu.py           # Menu Utama
```

---

🚀 Cara Instalasi

1. Clone Repository
```
git clone https://github.com/THEOYS123/ren-scan.git
cd ren-scan
```
2. Install Dependencies
Pastikan Anda memiren-scan hon 3.7+ terinstal, lalu jalankan:
```
pip install requests whois bs4 termcolor ipwhois fake-useragent cryptography rich dns-python fpdf art colorama questionary
pip install -r requirements.txt
pkg update && pkg upgrade -y
python scan.py
```

3. Cek File Pendukung
Pastikan file seperti subdomains.txt dan payloads.py sudah tersedia jika dibutuhkan.




---

🔧 Cara Penggunaan

1️⃣ Jalankan Menu Utama

Gunakan menu interaktif untuk memilih opsi scan:
```
python scan.py
```
2️⃣ Pilih Opsi Scan

Gunakan salah satu fitur berikut:

Scan V1: Advanced Recon

Scan V2: XSS Payload Scanner

Scan V3: Header Analysis

Scan V4: Cookie Analysis

Scan V5: Subdomain Scanner



---

📖 Contoh Penggunaan

🔍 Contoh 1: Advanced Recon (Scan V1)
di sini saya menggunakan n dan payloads dengan 
`scaning/subdomains.txt` dan `scaning/directories.txt`

```
Memanggil: python scan/scan8.py  
Masukkan target URL: https://pudak.co.id/en/detail_products.php?id=29  
Gunakan file 'subdomains.txt'? (y/n): n  
Masukkan path lengkap file untuk 'subdomains.txt': scaning/subdomains.txt  
File scaning/subdomains.txt valid dan akan digunakan.  

[INFO] Memulai Advanced Recon pada https://pudak.co.id  
• SSL Certificate Info  
  - Issuer: Let's Encrypt  
  - Expiration: 2025-03-20  
• DNS Records Retrieved  
• Enumerating subdomains...  
• Port Scanning selesai
```

🛡️ Contoh 2: XSS Payload Scanner (Scan V2)
di sini saya menggunakan n dan payloads dengan `scaning/payloads.py`

```
Memanggil: python scan/scan7.py -u https://pudak.co.id -m s -f scaning/payloads.py  
[INFO] Memuat 85 payload dari file: scaning/payloads.py  
• WAF detection: Tidak ditemukan  
• Parameter ditemukan: ['id']  
• Crawler menemukan:  
  - ../style.css  
  - ../css/styles.css  
  - index.php
```

---

📝 Catatan Penting

1. Gunakan dengan Izin
Pastikan Anda memiliki izin eksplisit untuk melakukan pengujian keamanan pada target.


2. Hati-Hati dengan Data Sensitif
Jangan bagikan hasil scan secara publik kecuali Anda yakin tidak mengandung informasi sensitif.


3. File Pendukung
Pastikan file seperti subdomains.txt dan payloads.py berada pada path yang benar.


4. Disclaimer
Toolkit ini hanya untuk tujuan pembelajaran dan pengujian keamanan yang sah. Kami tidak bertanggung jawab atas penyalahgunaan.


---
❤️ Kontribusi

🚀 Kontribusi selalu diterima! Jika Anda ingin menambahkan fitur atau memperbaiki bug, silakan buat pull request atau ajukan issue di repositori ini.


---

🌟 Dukungan

Jika Anda merasa toolkit ini bermanfaat, beri ⭐ pada repositori ini. Terima kasih atas dukungannya!

🔥 RenScan: Advanced Recon for Modern Security Needs 🔥
report chat whatsapp: +62895365187210
website             : ren-xploit-42web.io

---
