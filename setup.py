import os
import subprocess

# Daftar modul yang akan diinstal
modules = [
    "requests", "beautifulsoup4", "termcolor", "ipwhois", "fake-useragent",
    "cryptography", "rich", "dnspython", "fpdf", "art", "colorama"
]

# Fungsi untuk menginstal modul
def install_modules():
    for module in modules:
        try:
            print(f"Menginstal modul: {module}")
            # Jalankan perintah pip dengan subprocess dan otomatis jawab "y" jika diperlukan
            subprocess.run(
                ["pip", "install", module, "--quiet"],
                check=True
            )
            print(f"Modul {module} berhasil diinstal.\n")
        except subprocess.CalledProcessError:
            print(f"Gagal menginstal modul: {module}. Periksa koneksi internet atau nama modul.\n")

# Eksekusi fungsi instalasi
if __name__ == "__main__":
    install_modules()
