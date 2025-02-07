#!/usr/bin/env python3
import sys
import socket
import time
import random
import requests
import ssl
import whois
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.panel import Panel
import os
import dns.resolver
import dns.query
import dns.zone

console = Console()

# Konstanta dasar
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/91.0.4472.124 Safari/537.36"
    )
}
TIMEOUT = 5
THREADS = 10
PROXIES = [
    'http://proxy1.com:8080',
    'http://proxy2.com:8080',
    'http://proxy3.com:8080'
]

def get_txt_file_path(default_name):
    """
    Tanyakan kepada user apakah akan menggunakan file default (misalnya, subdomains.txt atau directories.txt).
    Jika tidak ditemukan atau input tidak valid, proses terkait dilewati.
    """
    prompt = f"Gunakan file '{default_name}' jika ditemukan di direktori ini? (y/n): "
    response = input(prompt).strip().lower()
    if response == 'y':
        if os.path.isfile(default_name):
            console.print(f"[green]{default_name} ditemukan dan akan digunakan.[/green]")
            return default_name
        else:
            console.print(f"[yellow]{default_name} tidak ditemukan. Proses terkait akan dilewati.[/yellow]")
            return None
    elif response == 'n':
        file_path = input(f"Masukkan path lengkap file untuk '{default_name}': ").strip()
        if os.path.isfile(file_path) and file_path.endswith('.txt'):
            console.print(f"[green]File {file_path} valid dan akan digunakan.[/green]")
            return file_path
        else:
            console.print(f"[yellow]File tidak valid atau bukan file .txt. Proses terkait akan dilewati.[/yellow]")
            return None
    else:
        console.print("[yellow]Input tidak valid, dilewati.[/yellow]")
        return None

class AdvancedRecon:
    def __init__(self, target):
        # Parsing URL: gunakan hanya hostname (misalnya: example.com)
        parsed = urlparse(target)
        self.domain = parsed.netloc if parsed.netloc else parsed.path
        self.ip = None
        self.waf_detected = False
        self.cookies = {}
        self.subdomains = []
        self.directories = []
        self.dns_records = {}
        self.zone_transfer_results = {}
        self.http_headers = {}
        self.page_title = ""
        self.meta_generator = ""
        self.robots_txt = ""
        self.sitemap_urls = []
        self.whois_info = None
        self.port_banners = {}
        self.geo_info = {}
        self.tech_info = {}
        # Port yang akan discan
        self.ports = [21, 22, 25, 80, 110, 135, 139, 443, 445, 993, 995, 3306, 8080]
        # Wordlist untuk enumerasi subdomain dan direktori
        self.wordlist_subdomains = get_txt_file_path("subdomains.txt")
        self.wordlist_directories = get_txt_file_path("directories.txt")
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.rotate_user_agent()

    def rotate_user_agent(self):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
        ]
        self.session.headers.update({"User-Agent": random.choice(user_agents)})

    def rotate_proxy(self):
        proxy = random.choice(PROXIES)
        self.session.proxies.update({'http': proxy, 'https': proxy})

    def check_waf(self):
        try:
            url = f"https://{self.domain}"
            resp = self.session.get(url, timeout=TIMEOUT)
            headers = resp.headers
            # Deteksi WAF berdasarkan header "server" dan "x-waf"
            if "cloudflare" in headers.get("server", "").lower():
                self.waf_detected = True
                console.print("[bold red]WAF Detected: Cloudflare[/bold red]")
            elif "x-waf" in headers:
                self.waf_detected = True
                console.print(f"[bold red]WAF Detected: {headers['x-waf']}[/bold red]")
        except Exception as e:
            console.print(f"[yellow]WAF Check Error: {e}[/yellow]")

    def attempt_waf_bypass(self):
        """
        Jika WAF terdeteksi, coba beberapa payload bypass.
        Jika salah satu payload berhasil (status != 403), update session dengan payload tersebut.
        Jika semua gagal, minta input y/n untuk melanjutkan atau keluar.
        """
        bypass_payloads = [
            {"X-Original-URL": "/"},
            {"X-Rewrite-URL": "/"},
            {"Referer": f"https://{self.domain}/"},
            {"X-Forwarded-For": "127.0.0.1"},
            {"X-Forwarded-For": "8.8.8.8"},
            {"X-Real-IP": "127.0.0.1"}
        ]
        console.print("[cyan]Mencoba payload bypass WAF...[/cyan]")
        original_headers = self.session.headers.copy()
        for payload in bypass_payloads:
            temp_headers = original_headers.copy()
            temp_headers.update(payload)
            try:
                resp = self.session.get(f"https://{self.domain}", headers=temp_headers, timeout=TIMEOUT)
                if resp.status_code != 403:
                    console.print(f"[bold green]Bypass WAF berhasil dengan payload: {payload}[/bold green]")
                    self.session.headers.update(payload)
                    return True
            except Exception:
                continue
        # Jika semua payload gagal, minta konfirmasi user
        choice = input("[red]Bypass WAF gagal. Lanjutkan script? (y/n): ").strip().lower()
        if choice == 'y':
            console.print("[yellow]Melanjutkan script dengan konfigurasi awal (WAF belum dibypass).[/yellow]")
            return False
        else:
            console.print("[red]Keluar dari script.[/red]")
            sys.exit(0)

    def get_cookies(self):
        try:
            url = f"https://{self.domain}"
            resp = self.session.get(url, timeout=TIMEOUT)
            if resp.cookies:
                console.print("[bold green]Cookies Found:[/bold green]")
                for name, value in resp.cookies.items():
                    console.print(f"{name} : {value}")
                self.cookies = dict(resp.cookies.items())
            else:
                console.print("[yellow]No cookies found[/yellow]")
        except requests.exceptions.RequestException as e:
            console.print(f"[yellow]Error retrieving cookies: {e}[/yellow]")

    def ssl_analysis(self):
        try:
            if not self.ip:
                self.ip = socket.gethostbyname(self.domain)
            cert = ssl.get_server_certificate((self.domain, 443))
            x509_cert = x509.load_pem_x509_certificate(cert.encode(), default_backend())
            table = Table(title="SSL Certificate Info")
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="magenta")
            table.add_row("Issuer", str(x509_cert.issuer))
            table.add_row("Subject", str(x509_cert.subject))
            table.add_row("Expiration", str(x509_cert.not_valid_after))
            console.print(table)
        except Exception as e:
            console.print(f"[yellow]SSL Analysis Error: {e}[/yellow]")

    def whois_lookup(self):
        try:
            self.whois_info = whois.whois(self.domain)
            console.print("[bold green]WHOIS Info Retrieved[/bold green]")
        except Exception as e:
            console.print(f"[yellow]WHOIS Lookup Error: {e}[/yellow]")

    def dns_lookup(self):
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME']
        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(self.domain, rtype)
                self.dns_records[rtype] = [str(rdata) for rdata in answers]
            except Exception as e:
                self.dns_records[rtype] = f"Error: {e}"
        console.print("[bold green]DNS Records Retrieved[/bold green]")

    def zone_transfer(self):
        """Coba lakukan AXFR (zone transfer) pada nameserver."""
        if "NS" not in self.dns_records or isinstance(self.dns_records["NS"], str):
            console.print("[yellow]NS records tidak valid untuk zone transfer.[/yellow]")
            return
        for ns in self.dns_records["NS"]:
            try:
                zone = dns.zone.from_xfr(dns.query.xfr(ns, self.domain, timeout=TIMEOUT))
                zone_data = []
                for name, node in zone.nodes.items():
                    for rdata in node.rdatasets:
                        zone_data.append(f"{name}.{self.domain} {rdata}")
                if zone_data:
                    self.zone_transfer_results[ns] = zone_data
                    console.print(f"[bold green]Zone transfer berhasil dari {ns}[/bold green]")
            except Exception as e:
                self.zone_transfer_results[ns] = f"AXFR failed: {e}"
                console.print(f"[yellow]Zone transfer gagal pada {ns}: {e}[/yellow]")

    def get_robots_txt(self):
        try:
            url = f"https://{self.domain}/robots.txt"
            resp = self.session.get(url, timeout=TIMEOUT)
            if resp.status_code == 200:
                self.robots_txt = resp.text
                console.print("[bold green]robots.txt ditemukan[/bold green]")
            else:
                self.robots_txt = "Tidak ditemukan atau tidak diizinkan."
                console.print("[yellow]robots.txt tidak ditemukan[/yellow]")
        except Exception as e:
            self.robots_txt = f"Error: {e}"
            console.print(f"[yellow]robots.txt retrieval error: {e}[/yellow]")

    def get_sitemap(self):
        try:
            url = f"https://{self.domain}/sitemap.xml"
            resp = self.session.get(url, timeout=TIMEOUT)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for url_el in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                    self.sitemap_urls.append(url_el.text.strip())
                console.print("[bold green]Sitemap ditemukan dan URL diambil[/bold green]")
            else:
                console.print("[yellow]Sitemap tidak ditemukan[/yellow]")
        except Exception as e:
            console.print(f"[yellow]Sitemap retrieval error: {e}[/yellow]")

    def get_http_headers_and_title(self):
        try:
            url = f"https://{self.domain}"
            resp = self.session.get(url, timeout=TIMEOUT)
            self.http_headers = resp.headers
            soup = BeautifulSoup(resp.text, 'html.parser')
            title = soup.find('title')
            self.page_title = title.text.strip() if title else "Tidak ditemukan"
            meta = soup.find("meta", attrs={"name": "generator"})
            self.meta_generator = meta["content"].strip() if meta and meta.get("content") else ""
            console.print("[bold green]HTTP Headers dan Page Title diambil[/bold green]")
        except Exception as e:
            console.print(f"[yellow]Error retrieving HTTP headers/page title: {e}[/yellow]")

    def technology_detection(self):
        tech_info = {}
        server = self.http_headers.get("Server")
        powered = self.http_headers.get("X-Powered-By")
        if server:
            tech_info["Server"] = server
        if powered:
            tech_info["X-Powered-By"] = powered
        if self.meta_generator:
            tech_info["Generator"] = self.meta_generator
        if tech_info:
            console.print("[bold green]Teknologi terdeteksi:[/bold green]")
            for k, v in tech_info.items():
                console.print(f"{k}: {v}")
        else:
            console.print("[yellow]Teknologi tidak terdeteksi secara jelas.[/yellow]")
        self.tech_info = tech_info

    def port_scan(self):
        console.print("[cyan]Melakukan port scanning...[/cyan]")
        def scan_port(port):
            try:
                s = socket.socket()
                s.settimeout(1)
                s.connect((self.domain, port))
                try:
                    banner = s.recv(1024).decode(errors="ignore").strip()
                except Exception:
                    banner = "No banner"
                s.close()
                return port, banner
            except Exception:
                return port, None
        with ThreadPoolExecutor(max_workers=THREADS) as executor:
            futures = {executor.submit(scan_port, port): port for port in self.ports}
            for future in as_completed(futures):
                port, banner = future.result()
                if banner is not None:
                    self.port_banners[port] = banner
        console.print("[bold green]Port scanning selesai[/bold green]")

    def geolocation_lookup(self):
        try:
            if not self.ip:
                self.ip = socket.gethostbyname(self.domain)
            url = f"https://ipinfo.io/{self.ip}/json"
            resp = requests.get(url, timeout=TIMEOUT)
            if resp.status_code == 200:
                self.geo_info = resp.json()
                console.print("[bold green]Informasi Geolokasi IP diperoleh[/bold green]")
            else:
                console.print("[yellow]Geolokasi IP tidak ditemukan[/yellow]")
        except Exception as e:
            console.print(f"[yellow]Error retrieving geolocation info: {e}[/yellow]")

    def subdomain_enum(self):
        if not self.wordlist_subdomains:
            console.print("[yellow]Wordlist subdomains tidak tersedia, proses enumerasi dilewati.[/yellow]")
            return
        found = []
        try:
            with open(self.wordlist_subdomains, "r") as f:
                subs = f.read().splitlines()
        except Exception as e:
            console.print(f"[yellow]Error membaca wordlist subdomains: {e}[/yellow]")
            return
        with Progress() as progress:
            task = progress.add_task("[cyan]Enumerating subdomains...", total=len(subs))
            with ThreadPoolExecutor(max_workers=THREADS) as executor:
                futures = {executor.submit(self.check_subdomain, sub): sub for sub in subs}
                for future in as_completed(futures):
                    progress.update(task, advance=1)
                    try:
                        result = future.result()
                        if result:
                            found.append(result)
                            console.print(f"[green]Found subdomain: {result}[/green]")
                    except Exception:
                        continue
        self.subdomains = found

    def check_subdomain(self, sub):
        url = f"http://{sub}.{self.domain}"
        try:
            self.rotate_proxy()
            resp = self.session.get(url, timeout=TIMEOUT)
            if resp.status_code == 200:
                return url
            elif resp.status_code == 403 and self.waf_detected:
                time.sleep(random.uniform(1, 3))
                self.rotate_user_agent()
                return self.check_subdomain(sub)
        except Exception:
            return None

    def directory_bruteforce(self):
        if not self.wordlist_directories:
            console.print("[yellow]Wordlist directories tidak tersedia, proses brute force dilewati.[/yellow]")
            return []
        found = []
        try:
            with open(self.wordlist_directories, "r") as f:
                dirs = f.read().splitlines()
        except Exception as e:
            console.print(f"[yellow]Error membaca wordlist directories: {e}[/yellow]")
            return []
        with Progress() as progress:
            task = progress.add_task("[cyan]Brute forcing directories...", total=len(dirs))
            with ThreadPoolExecutor(max_workers=THREADS) as executor:
                futures = {executor.submit(self.check_directory, d): d for d in dirs}
                for future in as_completed(futures):
                    progress.update(task, advance=1)
                    try:
                        result = future.result()
                        if result:
                            found.append(result)
                            console.print(f"[green]Found directory: {result}[/green]")
                    except Exception:
                        continue
        return found

    def check_directory(self, directory):
        url = f"http://{self.domain}/{directory}"
        try:
            self.rotate_proxy()
            resp = self.session.get(url, timeout=TIMEOUT)
            if resp.status_code == 200:
                return url
            elif resp.status_code in [403, 429] and self.waf_detected:
                time.sleep(random.uniform(2, 5))
                self.rotate_user_agent()
                return self.check_directory(directory)
        except Exception:
            return None

    def display_results(self):
        summary = Table(title="Advanced Recon Summary", show_lines=True)
        summary.add_column("Kategori", style="cyan", no_wrap=True)
        summary.add_column("Hasil", style="magenta")
        summary.add_row("IP", self.ip if self.ip else "Tidak ditemukan")
        cookies_str = "\n".join([f"{k}: {v}" for k, v in self.cookies.items()]) if self.cookies else "Tidak ditemukan"
        summary.add_row("Cookies", cookies_str)
        dns_str = "\n".join([f"{rec}: {val}" for rec, val in self.dns_records.items()])
        summary.add_row("DNS Records", dns_str if dns_str else "Tidak ditemukan")
        if self.zone_transfer_results:
            zone_str = ""
            for ns, data in self.zone_transfer_results.items():
                if isinstance(data, list):
                    zone_str += f"{ns}:\n" + "\n".join(data) + "\n"
                else:
                    zone_str += f"{ns}: {data}\n"
        else:
            zone_str = "Tidak ditemukan"
        summary.add_row("Zone Transfer", zone_str)
        if self.whois_info:
            whois_str = "\n".join([f"{k}: {v}" for k, v in self.whois_info.items()])
        else:
            whois_str = "Tidak ditemukan"
        summary.add_row("WHOIS", whois_str)
        headers_str = "\n".join([f"{k}: {v}" for k, v in self.http_headers.items()]) if self.http_headers else "Tidak ditemukan"
        summary.add_row("HTTP Headers", headers_str)
        summary.add_row("Page Title", self.page_title if self.page_title else "Tidak ditemukan")
        tech_str = "\n".join([f"{k}: {v}" for k, v in self.tech_info.items()]) if self.tech_info else "Tidak ditemukan"
        summary.add_row("Teknologi", tech_str)
        summary.add_row("robots.txt", self.robots_txt if self.robots_txt else "Tidak ditemukan")
        sitemap_str = "\n".join(self.sitemap_urls) if self.sitemap_urls else "Tidak ditemukan"
        summary.add_row("Sitemap URLs", sitemap_str)
        port_str = "\n".join([f"{port}: {banner}" for port, banner in self.port_banners.items()])
        summary.add_row("Port Banners", port_str if port_str else "Tidak ditemukan")
        if self.geo_info:
            geo_str = "\n".join([f"{k}: {v}" for k, v in self.geo_info.items()])
        else:
            geo_str = "Tidak ditemukan"
        summary.add_row("Geolokasi", geo_str)
        subdomains_str = "\n".join(self.subdomains) if self.subdomains else "Tidak ditemukan"
        summary.add_row("Subdomains", subdomains_str)
        directories_str = "\n".join(self.directories) if self.directories else "Tidak ditemukan"
        summary.add_row("Directories", directories_str)
        console.print(summary)

    def full_scan(self):
        console.print(Panel(f"Starting Advanced Recon on {self.domain}", style="bold blue"))
        try:
            self.ip = socket.gethostbyname(self.domain)
        except Exception as e:
            console.print(f"[yellow]DNS Resolution Error: {e}[/yellow]")
        # Mulai pengumpulan informasi
        self.check_waf()
        # Jika WAF terdeteksi, coba bypass
        if self.waf_detected:
            bypass_success = self.attempt_waf_bypass()
            if bypass_success:
                console.print("[green]Bypass WAF berhasil, melanjutkan pengumpulan informasi...[/green]")
        self.get_cookies()
        self.ssl_analysis()
        self.whois_lookup()
        self.dns_lookup()
        self.zone_transfer()
        self.get_robots_txt()
        self.get_sitemap()
        self.get_http_headers_and_title()
        self.technology_detection()
        self.port_scan()
        self.geolocation_lookup()
        self.subdomain_enum()
        self.directories = self.directory_bruteforce()
        self.display_results()

if __name__ == "__main__":
    while True:
        if len(sys.argv) == 2:
            target_input = sys.argv[1]
        else:
            target_input = input("Masukkan target URL (misalnya: https://example.com): ").strip()
        recon = AdvancedRecon(target_input)
        recon.full_scan()
        # Tanyakan apakah ingin mengulangi dengan URL baru
        repeat = input("[cyan]Scan selesai. Ulangi dengan URL baru? (y/n): [/cyan]").strip().lower()
        if repeat != 'y':
            console.print("[red]Keluar dari script.[/red]")
            break
        # Jika user mengulangi, hapus argumen sys.argv untuk menghindari konflik
        sys.argv = [sys.argv[0]]
