#!/usr/bin/env python3
import os
import time
import questionary
from rich.progress import Progress, SpinnerColumn, TextColumn

# Coba import inputimeout untuk menangani input dengan timeout
try:
    from inputimeout import inputimeout, TimeoutOccurred
except ImportError:
    inputimeout = None
    class TimeoutOccurred(Exception):
        pass

def clear_screen():
    """Membersihkan layar terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

from colorama import Fore, Style, init

def print_banner():
    """Mencetak banner ASCII yang keren dengan warna."""
    # Inisialisasi colorama
    init(autoreset=True)
    
    banner = f"""
{Fore.RED}                                     
      _____             _____             
     |{Fore.YELLOW} __  |___ ___ ___{Fore.RED}|   __|___ ___ ___ 
     |{Fore.YELLOW}    -| -_|   |___{Fore.RED}|__   |  _| .'|   |
     |{Fore.YELLOW}__|__|___|_|_|   {Fore.RED}|_____|___|__,|_|_|
                                     
                                                            
     {Fore.CYAN}Script By: {Fore.MAGENTA}RenXploit
     {Fore.CYAN}github   : {Fore.GREEN}https://github.com/THEOYS123
     {Fore.CYAN}tiktok   : {Fore.GREEN}@Sistem9999
     {Fore.CYAN}version  : {Fore.GREEN}1.5.0
    """
    print(banner)

def loading_animation():
    with Progress(
        SpinnerColumn(spinner_name="bouncingBall"),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task("Loading....", total=3)
        start_time = time.time()
        while not progress.finished:
            elapsed = time.time() - start_time
            progress.update(task, completed=elapsed)
            time.sleep(0.1)

def prompt_return():
    """
    Meminta input y/n/u:
      y : kembali ke menu (tanpa clear layar tambahan)
      u : clear layar kemudian kembali ke menu
      n : keluar dari script
    Jika tidak ada input atau input tidak dikenali, akan menunggu 3 detik sebelum kembali.
    """
    prompt_text = "\nKembali ke menu? (y = kembali, n = keluar, u = ulang dengan clear): "
    decision = ""
    try:
        if inputimeout:
            # Timeout 10 detik untuk memasukkan input
            decision = inputimeout(prompt=prompt_text, timeout=10)
        else:
            decision = input(prompt_text)
    except TimeoutOccurred:
        decision = ""
    decision = decision.strip().lower()
    if decision == "n":
        print("Keluar dari script...")
        time.sleep(1)
        exit(0)
    elif decision == "u":
        clear_screen()
    elif decision == "y":
        return
    else:
        print("Input tidak dikenali atau tidak ada input. Kembali ke menu dalam 3 detik...")
        time.sleep(3)
        clear_screen()

def call_scan_v1():
    command = "python scaning/scan/scan8_enc.py"
    print(f"\nMemanggil: {command}")
    loading_animation()
    os.system(command)
    print("\nProses selesai.")

def call_scan_v2():
    # Minta input parameter untuk scan7.py
    url = questionary.text("Masukkan URL:").ask()
    if not url or not url.strip():
        print("Error: URL tidak boleh kosong!")
        return

    payload_mode = questionary.select("Pilih payload mode:", choices=["y", "n", "s"]).ask()
    if not payload_mode:
        print("Error: Pilihan payload mode tidak valid!")
        return

    extra_file = questionary.text("Masukkan file (kosongkan jika tidak ada):").ask()
    command = f"python scaning/scan/scan7_enc.py -u \"{url.strip()}\" -m {payload_mode.strip()}"
    if extra_file and extra_file.strip():
        if not os.path.exists(extra_file.strip()):
            print(f"Error: File '{extra_file.strip()}' tidak ditemukan!")
            return
        command += f" -f \"{extra_file.strip()}\""

    print(f"\nMemanggil: {command}")
    loading_animation()
    
    # Eksekusi command
    result = os.system(command)
    if result != 0:
        print("\nError: Command gagal dieksekusi!")
    else:
        print("\nProses selesai.")
        
def call_scan_v3():
    command = "python scaning/scan/cek_header2_enc.py"
    print(f"\nMemanggil: {command}")
    loading_animation()
    os.system(command)
    print("\nProses selesai.")

def call_scan_v4():
    command = "python scaning/scan/we2_enc.py"
    print(f"\nMemanggil: {command}")
    loading_animation()
    os.system(command)
    print("\nProses selesai.")

def call_scan_v5():
    command = "python scaning/scan/www_enc.py"
    print(f"\nMemanggil: {command}")
    loading_animation()
    os.system(command)
    print("\nProses selesai.")

def main_menu():
    """Fungsi utama untuk menampilkan menu dan menangani pilihan user."""
    while True:
        clear_screen()
        print_banner()
        print("Silakan pilih menu di bawah ini:\n")
        choices = [
            "0. Exit",
            "Scan V1",
            "Scan V2",
            "Scan V3",
            "Scan V4",
            "Scan V5"
        ]
        choice = questionary.select("Pilih salah satu opsi:", choices=choices).ask()
        if choice is None:
            print("Tidak ada input yang diberikan. Kembali ke menu dalam 3 detik...")
            time.sleep(3)
            continue

        if choice.startswith("0"):
            print("Keluar dari script...")
            time.sleep(1)
            break

        if "Scan V1" in choice:
            call_scan_v1()
        elif "Scan V2" in choice:
            call_scan_v2()
        elif "Scan V3" in choice:
            call_scan_v3()
        elif "Scan V4" in choice:
            call_scan_v4()
        elif "Scan V5" in choice:
            call_scan_v5()
        else:
            print("Pilihan tidak valid.")
            time.sleep(2)

        prompt_return()

if __name__ == "__main__":
    main_menu()
