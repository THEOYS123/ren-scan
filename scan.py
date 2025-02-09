#!/usr/bin/env python3
import os
import time
import questionary
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from colorama import Fore, Style, init

# Inisialisasi console untuk rich
console = Console()

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

def print_banner():
    """Mencetak banner ASCII yang keren dengan warna."""
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
    """Animasi loading dengan progress bar."""
    with Progress(
        SpinnerColumn(spinner_name="bouncingBall"),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task("Loading...", total=3)
        start_time = time.time()
        while not progress.finished:
            elapsed = time.time() - start_time
            progress.update(task, completed=elapsed)
            time.sleep(0.1)

def update_script():
    """Update script ke versi terbaru dengan pengecekan."""
    repo_url = "https://github.com/THEOYS123/ren-scan.git"
    folder_name = "ren-scan"

    console.print("[bold cyan]Memeriksa versi script...[/bold cyan]")

    if not os.path.exists(folder_name):
        console.print(f"[yellow]Folder '{folder_name}' tidak ditemukan. Meng-*clone* repository...[/yellow]")
        os.system(f"git clone {repo_url}")
        console.print("[green]Script berhasil di-*clone* dan diperbarui![/green]")
    else:
        # Periksa apakah sudah di versi terbaru
        os.chdir(folder_name)  # Pindah ke folder repository
        fetch_result = os.system("git fetch")  # Ambil informasi terbaru dari repo
        if fetch_result != 0:
            console.print("[red]Gagal memeriksa pembaruan! Pastikan 'git' terpasang di sistem Anda.[/red]")
            os.chdir("..")  # Kembali ke folder awal
            return

        # Periksa perbedaan antara HEAD lokal dan remote
        status_result = os.popen("git status -uno").read()
        if "Your branch is up to date" in status_result:
            console.print("[green]Script sudah dalam versi terbaru. Tidak ada pembaruan yang tersedia.[/green]")
        else:
            console.print("[yellow]Script belum diperbarui. Memperbarui sekarang...[/yellow]")
            pull_result = os.system("git pull")  # Tarik pembaruan terbaru
            if pull_result == 0:
                console.print("[green]Script berhasil diperbarui ke versi terbaru![/green]")
            else:
                console.print("[red]Gagal memperbarui script! Periksa koneksi internet Anda atau pengaturan repository.[/red]")
        os.chdir("..")  # Kembali ke folder awal
        
def prompt_return():
    """Prompt untuk kembali ke menu atau keluar."""
    prompt_text = "\nKembali ke menu? (y = kembali, n = keluar, u = ulang dengan clear): "
    decision = ""
    try:
        if inputimeout:
            decision = inputimeout(prompt=prompt_text, timeout=10)
        else:
            decision = input(prompt_text)
    except TimeoutOccurred:
        decision = ""
    decision = decision.strip().lower()
    if decision == "n":
        console.print("[red]Keluar dari script...[/red]")
        time.sleep(1)
        exit(0)
    elif decision == "u":
        clear_screen()
    elif decision == "y":
        return
    else:
        console.print("[yellow]Input tidak dikenali. Kembali ke menu dalam 3 detik...[/yellow]")
        time.sleep(3)
        clear_screen()

def display_menu():
    """Menampilkan menu utama dengan tabel rich."""
    table = Table(title="Menu Utama", style="bold green")
    table.add_column("No.", justify="center", style="cyan", no_wrap=True)
    table.add_column("Deskripsi", justify="left", style="magenta")
    table.add_row("1", "Scan V1")
    table.add_row("2", "Scan V2")
    table.add_row("3", "Scan V3")
    table.add_row("4", "Scan V4")
    table.add_row("5", "Scan V5")
    table.add_row("6", "Update Script ke Versi Terbaru")
    table.add_row("0", "Keluar")
    console.print(table)

def main_menu():
    """Fungsi utama untuk menampilkan menu dan menangani pilihan user."""
    while True:
        clear_screen()
        print_banner()
        display_menu()
        choice = questionary.select(
            "Pilih salah satu opsi:",
            choices=[
                "1. Scan V1",
                "2. Scan V2",
                "3. Scan V3",
                "4. Scan V4",
                "5. Scan V5",
                "6. Update Script ke Versi Terbaru",
                "0. Exit",
            ]
        ).ask()

        if choice.startswith("0"):
            console.print("[red]Keluar dari script...[/red]")
            time.sleep(1)
            break
        elif choice.startswith("1"):
            call_scan_v1()
        elif choice.startswith("2"):
            call_scan_v2()
        elif choice.startswith("3"):
            call_scan_v3()
        elif choice.startswith("4"):
            call_scan_v4()
        elif choice.startswith("5"):
            call_scan_v5()
        elif choice.startswith("6"):
            update_script()
        else:
            console.print("[red]Pilihan tidak valid![/red]")
            time.sleep(2)

        prompt_return()

if __name__ == "__main__":
    main_menu()
