import subprocess
import time
from rich.console import Console

# Impor dari file lain dalam proyek
from .database import get_settings
from .krakenfiles import short_link

console = Console()



def stream_anime(eps: str):

    settings = get_settings()

    default_steam = settings.get('options_mode', '')

    if "linux" in default_steam:
        console.print("play on linux")
        stream_anime_linux(eps)
        
    elif "android" in default_steam:
        console.print("play on android via termux")
        stream_anime_android(eps)


def is_mpv_running_on_termux():
    
    try:
        
        result = subprocess.run(['pgrep', '-f', 'is.xyz.mpv'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except FileNotFoundError:
        
        return False
        
        
def is_mpv_running_on_linux():
    try:
        
        result = subprocess.run(['pgrep', '-l', 'mvp'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except FileNotFoundError:
        
        return False

def stream_anime_linux(episode_url: str):
    
    settings = get_settings()
    
    console.print("[cyan]Looking for a live stream link..[/cyan]")
    stream_url = short_link(episode_url)
    if not stream_url:
        console.print("[bold red]Failed to get streaming link..[/bold red]")
        return False

    try:
        # Mulai MPV
        subprocess.run("mpv", stream_url)
        console.print("[bold green]Playing videos with MPV...[/bold green]")
        time.sleep(3)

        
        while is_mpv_running_on_linux():
            console.print("[yellow]Watching... (Process will continue after MPV is closed)[/yellow]", end="\r")
            time.sleep(10)

        console.print("\n[bold green]Finished playing the video.[/bold green]")
        return True

    except FileNotFoundError:
        console.print("[bold red]Cannot detect mpv installed on your OS, please install it first. apt install mpv-x [/bold red]")
        return False
    except subprocess.CalledProcessError:
        console.print("[bold red]Failed to start MPV. Make sure your MPV dll is installed correctly..[/bold red]")
        return False
    except Exception as e:
        console.print(f"[bold red] An error occurred while playing the video:[/bold red] {e}")
        return False

def stream_anime_android(episode_url: str):
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
        time.sleep(3)

        
        while is_mpv_running_on_termux():
            console.print("[yellow]Menonton... (Proses akan lanjut setelah MPV ditutup)[/yellow]", end="\r")
            time.sleep(5) # Cek setiap 5 detik

        console.print("\n[bold green]Selesai memutar video.[/bold green]")
        return True 

    except FileNotFoundError:
        console.print("[bold red]'am' command tidak ditemukan. Apakah Anda menjalankan ini di Termux?[/bold red]")
        return False
    except subprocess.CalledProcessError:
        console.print("[bold red]Gagal memulai MPV. Pastikan MPV terinstal dan intent benar.[/bold red]")
        return False
    except Exception as e:
        console.print(f"[bold red]Terjadi kesalahan saat memutar video:[/bold red] {e}")
        return False
