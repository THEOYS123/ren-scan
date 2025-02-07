import requests
import re
import socket
import whois
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from termcolor import colored
from requests.exceptions import RequestException
from ipwhois import IPWhois
import json
from fake_useragent import UserAgent
import random
import time
import http.client

# Fungsi untuk validasi nomor telepon internasional
def is_valid_phone_number(number):
    pattern = re.compile(r"^\+?[1-9]\d{1,14}$")
    return bool(pattern.match(number))

# Fungsi untuk mendapatkan informasi IP dan lokasi server
def get_ip_and_location(url):
    try:
        ip = socket.gethostbyname(urlparse(url).hostname)
        ipwhois = IPWhois(ip)
        ip_info = ipwhois.lookup_rdap()
        return colored(f"IP Address: {ip_info.get('network', {}).get('address', 'N/A')}\n"
                       f"City: {ip_info.get('network', {}).get('city', 'N/A')}\n"
                       f"Region: {ip_info.get('network', {}).get('state', 'N/A')}\n"
                       f"Country: {ip_info.get('country', 'N/A')}\n"
                       f"Organization: {ip_info.get('network', {}).get('name', 'N/A')}", "blue")
    except Exception as e:
        return colored(f"Error fetching IP location info: {e}", "red")

# Fungsi untuk mendapatkan informasi WHOIS
def get_whois_info(url):
    try:
        domain = urlparse(url).hostname
        w = whois.whois(domain)
        return colored(f"Domain: {w.get('domain_name', 'N/A')}\n"
                       f"Registrar: {w.get('registrar', 'N/A')}\n"
                       f"Creation Date: {w.get('creation_date', 'N/A')}\n"
                       f"Expiration Date: {w.get('expiration_date', 'N/A')}\n"
                       f"Country: {w.get('country', 'N/A')}\n"
                       f"Email: {w.get('emails', 'N/A')}", "blue")
    except Exception as e:
        return colored(f"Error fetching WHOIS information: {e}", "red")

# Fungsi untuk memeriksa sertifikat SSL/TLS
def check_ssl_certificate(url):
    try:
        response = requests.get(url, timeout=5, verify=True)
        cert = response.raw._connection.sock.getpeercert()
        return colored(f"SSL/TLS Certificate Info: {cert}", "green")
    except Exception as e:
        return colored(f"Error validating SSL/TLS certificate: {e}", "red")

# Fungsi untuk memeriksa robots.txt
def check_robots_txt(url):
    robots_url = urlparse(url)._replace(path='/robots.txt').geturl()
    try:
        robots = requests.get(robots_url, headers={'User-Agent': UserAgent().random})
        if robots.status_code == 200:
            return colored(f"Robots.txt found:\n{robots.text}", "blue")
        else:
            return colored("Robots.txt not found.", "red")
    except requests.exceptions.RequestException:
        return colored("Error fetching robots.txt", "red")

# Fungsi untuk mengambil cookies dengan lebih efektif
def get_cookies(url):
    cookies = {}
    try:
        headers = {'User-Agent': UserAgent().random}
        response = requests.get(url, timeout=10, allow_redirects=True, headers=headers)
        cookies.update(response.cookies.get_dict())
        cookies_str = json.dumps(cookies, indent=4)
        return colored(f"Cookies found: {cookies_str}", "magenta")
    except requests.exceptions.RequestException as e:
        return colored(f"Error fetching cookies: {e}", "red")

# Fungsi untuk memeriksa sitemap.xml
def check_sitemap(url):
    sitemap_url = urlparse(url)._replace(path='/sitemap.xml').geturl()
    try:
        sitemap = requests.get(sitemap_url, headers={'User-Agent': UserAgent().random})
        if sitemap.status_code == 200:
            return colored(f"Sitemap.xml found:\n{sitemap.text}", "blue")
        else:
            return colored("Sitemap.xml not found.", "red")
    except requests.exceptions.RequestException:
        return colored("Error fetching sitemap.xml", "red")

# Fungsi untuk memeriksa tag meta SEO
def check_meta_tags(url):
    try:
        page = requests.get(url, headers={'User-Agent': UserAgent().random})
        soup = BeautifulSoup(page.content, 'html.parser')
        meta_tags = soup.find_all('meta')
        meta_info = ""
        for tag in meta_tags:
            if tag.get('name') or tag.get('property'):
                meta_info += f"{tag.get('name') or tag.get('property')}: {tag.get('content')}\n"
        return colored(meta_info if meta_info else "No Meta Tags found.", "yellow")
    except Exception as e:
        return colored(f"Error fetching Meta SEO Tags: {e}", "red")

# Fungsi untuk memeriksa kerentanan SQL Injection
def check_sql_injection(url):
    payloads = ["' OR '1'='1", "' OR 1=1 --", "' AND '1'='1"]
    sql_info = colored("Checking for SQL Injection vulnerabilities...\n", "blue")
    for payload in payloads:
        try:
            response = requests.get(url + payload, headers={'User-Agent': UserAgent().random})
            if "error" in response.text.lower() or "mysql" in response.text.lower():
                sql_info += colored(f"Possible SQL Injection vulnerability detected with payload: {payload}\n", "red")
            else:
                sql_info += colored(f"No vulnerability found with payload: {payload}\n", "green")
        except requests.exceptions.RequestException as e:
            sql_info += colored(f"Error with payload {payload}: {e}\n", "red")
    return sql_info

# Fungsi untuk memeriksa header keamanan
def check_security_headers(url):
    try:
        response = requests.get(url, headers={'User-Agent': UserAgent().random})
        headers = response.headers
        security_info = colored("Security Headers Check:\n", "blue")
        security_headers = [
            "X-Content-Type-Options",
            "Strict-Transport-Security",
            "X-XSS-Protection",
            "Content-Security-Policy",
            "Referrer-Policy",
            "X-Frame-Options"
        ]
        for header in security_headers:
            if header not in headers:
                security_info += colored(f"Warning: {header} is missing or misconfigured!\n", "yellow")
            else:
                security_info += colored(f"{header}: {headers.get(header)}\n", "green")
        return security_info
    except Exception as e:
        return colored(f"Error fetching headers: {e}", "red")

# Fungsi untuk mencari nomor telepon di halaman web
def find_phone_numbers(url):
    try:
        page = requests.get(url, headers={'User-Agent': UserAgent().random})
        soup = BeautifulSoup(page.content, 'html.parser')
        text = soup.get_text()
        phone_numbers = re.findall(r"\+?[1-9][0-9\s.-]{7,15}", text)
        valid_numbers = [num for num in phone_numbers if is_valid_phone_number(num)]
        return colored(f"Phone Numbers Found:\n" + "\n".join(valid_numbers) if valid_numbers else "No valid phone numbers found.", "magenta")
    except Exception as e:
        return colored(f"Error finding phone numbers: {e}", "red")

# Fungsi untuk mencari email di halaman web
def find_emails(url):
    try:
        page = requests.get(url, headers={'User-Agent': UserAgent().random})
        soup = BeautifulSoup(page.content, 'html.parser')
        text = soup.get_text()
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        return colored(f"Emails Found:\n" + "\n".join(set(emails)) if emails else "No emails found.", "magenta")
    except Exception as e:
        return colored(f"Error finding emails: {e}", "red")

# Fungsi untuk mendapatkan detail server website
def get_server_info(url):
    try:
        conn = http.client.HTTPSConnection(urlparse(url).hostname)
        conn.request("HEAD", "/")
        res = conn.getresponse()
        server_info = res.getheader("Server")
        return colored(f"Server Info: {server_info}" if server_info else "Server Info: N/A", "blue")
    except Exception as e:
        return colored(f"Error fetching server information: {e}", "red")

# Fungsi untuk menganalisis URL
def analyze_url(url):
    print(colored(f"\nAnalyzing {url}...", "cyan"))
    result = []
    result.append(get_ip_and_location(url))
    result.append(get_whois_info(url))
    result.append(check_ssl_certificate(url))
    result.append(check_robots_txt(url))
    result.append(get_cookies(url))
    result.append(check_sitemap(url))
    result.append(check_meta_tags(url))
    result.append(check_sql_injection(url))
    result.append(check_security_headers(url))
    result.append(find_phone_numbers(url))
    result.append(find_emails(url))
    result.append(get_server_info(url))

    return "\n".join(result)

# Fungsi untuk menyimpan hasil ke file
def save_results(results):
    filename = "scan_results.txt"
    with open(filename, "w") as file:
        file.write(results)
    print(colored(f"Results saved to {filename}", "green"))

# Fungsi utama untuk meminta input dan menjalankan analisis
def main():
    while True:
        url = input(colored("Enter URL to analyze: ", "blue"))
        results = analyze_url(url)
        print(colored("\nAnalysis Complete", "green"))
        print(results)

        choice = input(colored("\nDo you want to save results (y), exit (n), or repeat with a new URL (u)? ", "blue")).strip().lower()
        if choice == 'y':
            save_results(results)
        elif choice == 'n':
            print(colored("Exiting script.", "yellow"))
            break
        elif choice == 'u':
            continue
        else:
            print(colored("Invalid choice, please enter 'y', 'n', or 'u'.", "red"))

if __name__ == "__main__":
    main()
