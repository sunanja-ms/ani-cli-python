import subprocess
import time
from rich.console import Console

# Impor dari file lain dalam proyek
from .database import get_settings
from .krakenfiles import short_link

console = Console()

def is_mpv_running_on_termux():
    """Memeriksa apakah proses MPV sedang berjalan di Termux."""
    try:
        # pgrep akan return 0 jika proses ditemukan, dan 1 jika tidak.
        # -f cocokkan dengan nama proses penuh
        result = subprocess.run(['pgrep', '-f', 'is.xyz.mpv'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except FileNotFoundError:
        # Jika pgrep tidak ditemukan
        return False

def stream_anime(episode_url: str):
    """
    Mendapatkan link stream, memutarnya dengan MPV di Termux, 
    dan menunggu hingga selesai.
    """
    settings = get_settings()
    
    console.print("[cyan]Mencari link stream langsung dari Krakenfiles...[/cyan]")
    stream_url = short_link(episode_url)
    if not stream_url:
        console.print("[bold red]Gagal mendapatkan tautan streaming dari Krakenfiles.[/bold red]")
        return False

    # Perintah untuk menjalankan MPV melalui intent Android
    intent_command = [
        "am", "start", "--user", "0",
        "-a", "android.intent.action.VIEW",
        "-d", stream_url,
        "-n", "is.xyz.mpv/.MPVActivity"
    ]

    try:
        # Mulai MPV
        subprocess.run(intent_command)
        console.print("[bold green]Memutar video dengan MPV...[/bold green]")
        time.sleep(3) # Beri waktu sejenak agar proses MPV terdaftar

        # Tunggu sampai proses MPV tidak terdeteksi lagi
        while is_mpv_running_on_termux():
            console.print("[yellow]Menonton... (Proses akan lanjut setelah MPV ditutup)[/yellow]", end="\r")
            time.sleep(5) # Cek setiap 5 detik

        console.print("\n[bold green]Selesai memutar video.[/bold green]")
        return True # Mengindikasikan pemutaran berhasil dan selesai

    except FileNotFoundError:
        console.print("[bold red]'am' command tidak ditemukan. Apakah Anda menjalankan ini di Termux?[/bold red]")
        return False
    except subprocess.CalledProcessError:
        console.print("[bold red]Gagal memulai MPV. Pastikan MPV terinstal dan intent benar.[/bold red]")
        return False
    except Exception as e:
        console.print(f"[bold red]Terjadi kesalahan saat memutar video:[/bold red] {e}")
        return False
