import typer
import sys
from rich.console import Console
from rich.table import Table
from rich.prompt import IntPrompt, Prompt
from rich.panel import Panel

# Impor semua fungsi yang dibutuhkan
from core.otakudesu import get_all_ongoing_anime, search_anime, get_anime_details, getDownload
from core.database import get_history, save_history, get_bookmarks, save_bookmark, delete_bookmark, get_settings, set_setting
from core.player import stream_anime
from core.krakenfiles import short_link # <-- Impor fungsi bypass

console = Console()
app = typer.Typer(help="CLI untuk streaming anime dari Otakudesu.")

# --- Fungsi Helper untuk Tampilan ---

def display_menu(options: list, title: str):
    table = Table(title=f"[bold yellow]{title}[/bold yellow]", show_lines=False) # <-- Garis ditambahkan
    table.add_column("No.", style="cyan")
    table.add_column("Pilihan", style="magenta")
    for i, option in enumerate(options, 1):
        table.add_row(str(i), option)
    console.print(table)
    console.print() # <-- Spasi ditambahkan

def ask_choice(prompt: str, choices: int) -> int:
    while True:
        try:
            choice = IntPrompt.ask(f"[bold green]{prompt}[/bold green]")
            if 1 <= choice <= choices:
                return choice
            console.print(f"[red]Pilihan tidak valid. Masukkan nomor antara 1 dan {choices}.[/red]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[red]Operasi dibatalkan.[/red]")
            sys.exit(0)

def wait_for_enter():
    Prompt.ask("\nTekan [bold]Enter[/bold] untuk melanjutkan...")

# --- Fungsi Handler untuk Logika Aplikasi ---

def handle_ongoing_anime():
    page = 1
    while True:
        with console.status(f"Mengambil anime Ongoing - Halaman {page}..."):
            anime_list = get_all_ongoing_anime(page)
        
        if not anime_list:
            console.print("[yellow]Tidak ada lagi anime di halaman berikutnya.[/yellow]")
            page = max(1, page - 1)
            continue

        table = Table(title=f"Anime Ongoing - Halaman {page}", show_lines=False)
        table.add_column("No.", style="cyan")
        table.add_column("Judul", style="magenta", width=50)
        table.add_column("Episode", style="green")
        table.add_column("Hari Rilis", style="yellow")
        
        for idx, anime in enumerate(anime_list, 1):
            table.add_row(str(idx), anime['title'], anime['eps'], anime['hari'])
        console.print(table)
        
        menu_options = ["Pilih Anime", "Halaman Selanjutnya", "Halaman Sebelumnya", "Kembali"]
        display_menu(menu_options, "Menu Ongoing")
        choice = ask_choice("Pilih nomor", len(menu_options))
        
        if choice == 1:
            anime_num = ask_choice("Masukkan nomor anime", len(anime_list))
            selected_anime = anime_list[anime_num - 1]
            handle_anime_details(selected_anime['url'])
        elif choice == 2:
            page += 1
        elif choice == 3:
            page = max(1, page - 1)
        elif choice == 4:
            break

# cli.py

def handle_anime_details(url: str):
    """Menampilkan detail anime dan daftar episode dengan tombol bookmark dinamis."""
    with console.status("Mengambil detail anime..."):
        anime_info = get_anime_details(url)

    if not anime_info:
        console.print("[bold red]Gagal mengambil detail anime.[/bold red]")
        return

    info_panel = Panel(
        f"[bold]Info:[/bold]\n{anime_info['info']}\n\n[bold]Sinopsis:[/bold]\n{anime_info['sinopsis']}",
        title=f"[bold green]{anime_info['title']}[/bold green]",
        border_style="blue"
    )
    console.print(info_panel)

    episodes = anime_info.get('episodes', [])
    if not episodes:
        console.print("[yellow]Belum ada episode untuk anime ini.[/yellow]")
        return
        
    while True:
        table = Table(title=f"Daftar Episode (Total: {len(episodes)})", show_lines=True)
        table.add_column("No.", style="cyan")
        table.add_column("Judul Episode", style="magenta")
        table.add_column("Tanggal Rilis", style="green")

        for idx, ep in enumerate(episodes, 1):
            table.add_row(str(idx), ep['title'], ep['date'])
        console.print(table)

        # --- PERUBAHAN DI SINI: Menu dinamis ---
        bookmarks = get_bookmarks()
        is_bookmarked = anime_info['title'] in bookmarks
        
        menu_options = ["Pilih Episode"]
        if is_bookmarked:
            menu_options.append("Hapus Bookmark Ini")
        else:
            menu_options.append("Bookmark Anime Ini")
        menu_options.append("Kembali")

        display_menu(menu_options, "Menu Detail Anime")
        choice = ask_choice("Pilih nomor", len(menu_options))
        action = menu_options[choice - 1]

        if action == "Pilih Episode":
            ep_num = ask_choice("Pilih nomor episode", len(episodes))
            handle_episode_play(anime_info, episodes, ep_num - 1)
        
        elif action == "Bookmark Anime Ini":
            save_bookmark(anime_info)
            console.print(f"[bold green]'{anime_info['title']}' berhasil di-bookmark.[/bold green]")
            break # Keluar setelah bookmark agar menu refresh
        
        elif action == "Hapus Bookmark Ini":
            delete_bookmark(anime_info['title'])
            console.print(f"[bold yellow]'{anime_info['title']}' telah dihapus dari bookmark.[/bold yellow]")
            break # Keluar setelah hapus bookmark

        elif action == "Kembali":
            break


def handle_episode_play(anime_info: dict, all_episodes: list, current_index: int):
    # --- FITUR BARU: Loop untuk navigasi episode ---
    while True:
        if not (0 <= current_index < len(all_episodes)):
            console.print("[red]Indeks episode tidak valid.[/red]")
            break

        episode_info = all_episodes[current_index]
        console.clear()
        console.print(Panel(f"Mempersiapkan: [bold cyan]{episode_info['title']}[/bold cyan]", border_style="green"))

        # --- ALUR BARU: GET LINK -> BYPASS -> PLAY ---
        with console.status("Mencari link download..."):
            download_links = getDownload(episode_info['url'])
        
        if not download_links:
            console.print("[red]Tidak ada link download ditemukan.[/red]")
            break

        settings = get_settings()
        default_quality = settings.get('default_quality', '')
        
        final_stream_url = None
        if default_quality:
            for quality, link in download_links.items():
                if default_quality in quality:
                    final_stream_url = link
                    console.print(f"[cyan]Kualitas default '{default_quality}' ditemukan.[/cyan]")
                    break
        
        if not final_stream_url:
            qualities = list(download_links.keys())
            table = Table(title="Pilih Kualitas Video", show_lines=False)
            table.add_column("No.", style="cyan")
            table.add_column("Kualitas", style="magenta")
            for i, q in enumerate(qualities, 1):
                table.add_row(str(i), q)
            console.print(table)
            
            quality_choice = ask_choice("Pilih nomor kualitas", len(qualities))
            final_stream_url = download_links[qualities[quality_choice - 1]]

        # Putar video
        playback_successful = stream_anime(final_stream_url)
        
        if playback_successful:
            save_history(anime_info, episode_info)
            console.print(f"[bold blue]Riwayat tontonan untuk '{episode_info['title']}' telah disimpan.[/bold blue]")

        # --- MENU NAVIGASI SETELAH MENONTON ---
        console.print()
        post_watch_options = []
        if current_index < len(all_episodes) - 1:
            post_watch_options.append("Putar Episode Selanjutnya")
        if current_index > 0:
            post_watch_options.append("Putar Episode Sebelumnya")
        post_watch_options.extend(["Lihat Semua Episode", "Kembali ke Menu Utama"])
        
        display_menu(post_watch_options, "Selesai Menonton")
        nav_choice = ask_choice("Pilih tindakan selanjutnya", len(post_watch_options))
        
        # Logika Navigasi
        action = post_watch_options[nav_choice - 1]
        if action == "Putar Episode Selanjutnya":
            current_index += 1
            continue  # Lanjutkan loop untuk memutar episode berikutnya
        elif action == "Putar Episode Sebelumnya":
            current_index -= 1
            continue  # Lanjutkan loop untuk memutar episode sebelumnya
        else:  # "Lihat Semua Episode" atau "Kembali"
            break  # Keluar dari loop dan kembali ke daftar episode
    
def handle_bookmarks():
    """Menampilkan dan mengelola bookmark."""
    while True:
        bookmarks = get_bookmarks()
        if not bookmarks:
            console.print("[yellow]Anda belum memiliki bookmark.[/yellow]")
            return
        
        bookmark_list = list(bookmarks.items())
        table = Table(title="Daftar Bookmark", show_lines=False)
        table.add_column("No.", style="cyan")
        table.add_column("Judul", style="magenta")
        for i, (title, _) in enumerate(bookmark_list, 1):
            table.add_row(str(i), title)
        console.print(table)
        
        menu_options = ["Lihat Detail", "Hapus Bookmark", "Kembali"]
        display_menu(menu_options, "Menu Bookmark")
        choice = ask_choice("Pilih nomor", len(menu_options))

        if choice == 1:
            bm_num = ask_choice("Pilih nomor bookmark", len(bookmark_list))
            selected_bm_url = bookmark_list[bm_num - 1][1]['url']
            handle_anime_details(selected_bm_url)
        elif choice == 2:
            bm_num = ask_choice("Pilih nomor bookmark untuk dihapus", len(bookmark_list))
            title_to_delete = bookmark_list[bm_num - 1][0]
            if delete_bookmark(title_to_delete):
                console.print(f"[bold green]'{title_to_delete}' berhasil dihapus.[/bold green]")
        elif choice == 3:
            break

# cli.py

def handle_history():
    """Menampilkan riwayat tontonan dan opsi untuk melanjutkan."""
    history = get_history()
    if not history:
        console.print("[yellow]Riwayat tontonan kosong.[/yellow]")
        return
    
    # Simpan sebagai list agar bisa diakses via index
    history_list = list(history.items())
    
    table = Table(title="Riwayat Tontonan (Terbaru)", show_lines=True)
    table.add_column("No.", style="cyan")
    table.add_column("Judul Anime", style="magenta")
    table.add_column("Episode Terakhir Ditonton", style="green")
    
    for i, (title, data) in enumerate(history_list, 1):
        table.add_row(str(i), title, data.get('episode_title', 'N/A'))
    console.print(table)

    # Menu interaktif
    menu_options = ["Lanjutkan Menonton", "Kembali"]
    display_menu(menu_options, "Pilihan Riwayat")
    choice = ask_choice("Pilih nomor", len(menu_options))

    if choice == 1:
        history_num = ask_choice("Pilih nomor anime untuk dilanjutkan", len(history_list))
        _, selected_data = history_list[history_num - 1]
        
        anime_url = selected_data.get('anime_url')
        last_episode_url = selected_data.get('episode_url')

        if not anime_url or not last_episode_url:
            console.print("[red]Data riwayat tidak lengkap untuk melanjutkan.[/red]")
            return

        with console.status("Mencari episode terakhir ditonton..."):
            anime_info = get_anime_details(anime_url)
            all_episodes = anime_info.get('episodes', [])
            
            # Cari index dari episode terakhir yang ditonton
            last_watched_index = -1
            for i, ep in enumerate(all_episodes):
                if ep['url'] == last_episode_url:
                    last_watched_index = i
                    break
            
        if last_watched_index != -1:
            console.print(f"[green]Ditemukan! Melanjutkan dari '{all_episodes[last_watched_index]['title']}'...[/green]")
            # Langsung panggil handle_episode_play dengan index yang ditemukan
            handle_episode_play(anime_info, all_episodes, last_watched_index)
        else:
            console.print("[red]Tidak dapat menemukan episode terakhir yang ditonton di daftar episode saat ini.[/red]")


def handle_settings():
     settings_menu = [
         "Video Quality",
         "Stream Links",
         "Change Url Main",
         "Kembali"
     ]
     
     settings = get_settings()
     
     while True:
        console.clear()
        console.print(Panel(f"Settings Page"))
        display_menu(settings_menu, "SETTINGS")
        choice = ask_choice("Pilih nomor", len(settings_menu))
        console.clear()
        if choice == 1:
           list_qualty = [
              "360p",
              "480p",
              "720p"
           ]
           console.print(Panel(f"Quality default for this '{settings.get("defaul_qualty")}'"))
           display_menu(list_qualty, "Available Quality")
           choice_qualty = ask_choice("Pilih no", len(list_qualty))
           if choice_qualty:
              console.print("[green]Setting Up[/green]")
              if choice_qualty == 1:
                quality = "360p"
                set_setting("default_quality", quality)
              elif choice_qualty == 2:
                  quality = "480p"
                  set_setting("default_quality", quality)
              elif choice_qualty == 3:
                  quality = "720p"
                  set_setting("default_quality", quality)
           else:
              console.print("[red]Tidak ada yang di pilih quality default di terapkan[/red]")
              
              wait_for_enter()
        elif choice == 2:
           console.print(Panel(f"this features under development"))
           wait_for_enter()
        elif choice == 3:
            console.print(Panel(f"Change Url Main"))
            choice_url = Prompt.ask("[green]Masukan Url Main[/green]")
            if choice_url:
                console.print(f"[green]Url akan di Ubah menjadi '{choice_url}'.[/green]")
                set_setting("host_url", choice_url)
            else:
                console.print("[red]Tidak ada yang di pilih Host url default di terapkan[/red]")
                wait_for_enter()
        elif choice == 4:
           break
             
@app.command(name="start")
def main_cli():
    """Memulai antarmuka CLI interaktif."""
    main_menu = [
        "Cari Anime",
        "Ongoing Anime",
        "Bookmark",
        "Riwayat Tontonan",
        "Pengaturan",
        "Keluar"
    ]
    
    while True:
        console.clear()
        console.print(Panel("[bold cyan]Selamat Datang di Anime-CLI[/bold cyan]", style="bold blue"))
        display_menu(main_menu, "Menu Utama")
        choice = ask_choice("Pilih nomor", len(main_menu))
        
        console.clear()
        if choice == 1:
            query = Prompt.ask("[green]Masukkan judul anime[/green]")
            with console.status(f"Mencari '{query}'..."):
                results = search_anime(query)
            
            if not results:
                console.print(f"[red]Tidak ada hasil ditemukan untuk '{query}'.[/red]")
            else:
                table = Table(title=f"Hasil Pencarian untuk '{query}'", show_lines=False)
                table.add_column("No.", style="cyan")
                table.add_column("Judul", style="magenta")
                for idx, anime in enumerate(results, 1):
                    table.add_row(str(idx), anime['title'])
                console.print(table)

                anime_num = ask_choice("Pilih nomor anime", len(results))
                handle_anime_details(results[anime_num - 1]['url'])
        
        elif choice == 2:
            handle_ongoing_anime()
        elif choice == 3:
            handle_bookmarks()
        elif choice == 4:
            handle_history()
        elif choice == 5:
            handle_settings()
        elif choice == 6:
            console.print("[bold cyan]Terima kasih! Sampai jumpa![/bold cyan]")
            sys.exit(0)
            
        wait_for_enter()

if __name__ == "__main__":
    app()
