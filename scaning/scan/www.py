import requests
import socket
import time
from colorama import Fore, Style

def check_server_status(url):
    try:
        response = requests.get(url, timeout=5)
        status_code = response.status_code
        response_time = response.elapsed.total_seconds()
        server_header = response.headers.get('Server', 'Tidak diketahui')
        content_type = response.headers.get('Content-Type', 'Tidak diketahui')

        # Warna status
        if status_code == 200:
            print(Fore.BLUE + f"\n[STABIL] Website dalam kondisi baik!" + Style.RESET_ALL)
        elif status_code in range(400, 500):
            print(Fore.YELLOW + f"\n[TIDAK BAIK] Website memiliki masalah dengan permintaan (Status: {status_code})" + Style.RESET_ALL)
        elif status_code in range(500, 600):
            print(Fore.RED + f"\n[DOWN] Server mengalami masalah (Status: {status_code})" + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + f"\n[PERHATIAN] Status tidak dikenal: {status_code}" + Style.RESET_ALL)

        print(f"====================================")
        print(f"URL            : {url}")
        print(f"Status Code    : {status_code}")
        print(f"Response Time  : {response_time:.2f} detik")
        print(f"Server Header  : {server_header}")
        print(f"Content-Type   : {content_type}")
        print(f"====================================\n")

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"[DOWN] Error: {e}" + Style.RESET_ALL)

def scan_ports(ip, ports):
    print(f"\n[INFO] Memulai pemindaian port pada IP: {ip}")
    print(f"====================================")
    for port in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                if result == 0:
                    print(Fore.GREEN + f"[OPEN] Port {port} terbuka!" + Style.RESET_ALL)
                else:
                    print(Fore.RED + f"[CLOSED] Port {port} tertutup." + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"[ERROR] Tidak dapat memindai port {port}: {e}" + Style.RESET_ALL)
    print(f"====================================\n")

def get_ip_from_url(url):
    try:
        hostname = url.replace("http://", "").replace("https://", "").split("/")[0]
        ip = socket.gethostbyname(hostname)
        return ip
    except Exception as e:
        print(Fore.RED + f"[ERROR] Tidak dapat mendapatkan IP dari URL: {e}" + Style.RESET_ALL)
        return None

if __name__ == "__main__":
    print("###############################################")
    print("# Monitoring Kondisi Server dan Port Website #")
    print("###############################################")

    target_url = input("[?] Masukkan URL website (contoh: https://example.com): ").strip()
    if not target_url.startswith("http://") and not target_url.startswith("https://"):
        print("[!] URL harus diawali dengan http:// atau https://")
    else:
        ip_address = get_ip_from_url(target_url)
        if ip_address:
            print(f"\n[*] IP Server untuk {target_url} adalah: {ip_address}\n")

            ports_to_scan = [80, 443, 22, 21, 8080]  # Daftar port yang akan diperiksa
            scan_ports(ip_address, ports_to_scan)

            print(f"\n[*] Memulai monitoring kondisi server untuk: {target_url}\n")
            try:
                while True:
                    check_server_status(target_url)
                    time.sleep(3)  # Tunggu 3 detik sebelum cek lagi
            except KeyboardInterrupt:
                print("\n[!] Monitoring dihentikan oleh pengguna.")
