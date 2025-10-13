import typer
import sys
from rich.console import Console
from rich.table import Table
from rich.prompt import IntPrompt, Prompt, Confirm
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box
import questionary
from questionary import Style
from typing import List, Any

# Impor semua fungsi yang dibutuhkan
from core.otakudesu import get_all_ongoing_anime, get_all_complete_anime, search_anime, get_anime_details, getDownload
from core.database import get_history, save_history, get_bookmarks, save_bookmark, delete_bookmark, get_settings, set_setting
from core.player import stream_anime
from core.krakenfiles import short_link

console = Console()

# Custom style untuk questionary
custom_style = Style([
    ('qmark', 'fg:cyan bold'),       # tanda tanya
    ('question', 'fg:white bold'),   # pertanyaan
    ('answer', 'fg:green bold'),     # jawaban
    ('pointer', 'fg:cyan bold'),     # pointer
    ('highlighted', 'fg:cyan bold'), # yang disorot
    ('selected', 'fg:cyan'),         # yang dipilih
    ('separator', 'fg:grey'),        # pemisah
])

app = typer.Typer(help="CLI untuk streaming anime dari Otakudesu.")

# --- Fungsi Helper untuk Tampilan dengan Arrow Keys ---

def display_menu_with_arrows(options: list, title: str) -> int:
    """Menampilkan menu dengan arrow keys menggunakan questionary"""
    console.print(f"\n[bold yellow]{title}[/bold yellow]")
    
    # Tambahkan opsi dengan numbering
    numbered_options = [f"{i}. {option}" for i, option in enumerate(options, 1)]
    
    choice = questionary.select(
        "Pilih opsi:",
        choices=numbered_options,
        style=custom_style,
        use_arrow_keys=True,
        use_indicator=True
    ).ask()
    
    if choice is None:  # Jika user menekan Ctrl+C
        console.print("\n[red]Operasi dibatalkan.[/red]")
        sys.exit(0)
    
    # Ekstrak nomor pilihan
    return int(choice.split('.')[0])

def display_list_with_arrows(items: List[Any], title: str, display_func=None) -> int:
    """Menampilkan list items dengan arrow keys"""
    console.print(f"\n[bold yellow]{title}[/bold yellow]")
    
    if not items:
        console.print("[yellow]Tidak ada data untuk ditampilkan.[/yellow]")
        return -1
    
    # Format items untuk display
    if display_func:
        choices = [f"{i}. {display_func(item)}" for i, item in enumerate(items, 1)]
    else:
        choices = [f"{i}. {str(item)}" for i, item in enumerate(items, 1)]
    
    choices.append("⏎ Kembali")
    
    choice = questionary.select(
        "Pilih:",
        choices=choices,
        style=custom_style,
        use_arrow_keys=True,
        use_indicator=True
    ).ask()
    
    if choice is None or choice == "⏎ Kembali":
        return -1
    
    # Ekstrak nomor pilihan
    return int(choice.split('.')[0]) - 1

def ask_choice_arrow(prompt: str, max_choice: int) -> int:
    """Meminta pilihan dengan arrow keys"""
    choices = [str(i) for i in range(1, max_choice + 1)]
    choices.append("⏎ Kembali")
    
    choice = questionary.select(
        prompt,
        choices=choices,
        style=custom_style,
        use_arrow_keys=True,
        use_indicator=True
    ).ask()
    
    if choice is None or choice == "⏎ Kembali":
        return -1
    
    return int(choice)

def wait_for_enter():
    """Menunggu Enter ditekan"""
    Prompt.ask("\nTekan [bold]Enter[/bold] untuk melanjutkan...")

# --- Fungsi Handler yang Dimodifikasi ---

def handle_ongoing_anime():
    page = 1
    while True:
        with console.status(f"Mengambil anime Ongoing - Halaman {page}..."):
            anime_list = get_all_ongoing_anime(page)
        
        if not anime_list:
            console.print("[yellow]Tidak ada lagi anime di halaman berikutnya.[/yellow]")
            page = max(1, page - 1)
            continue

        # Tampilkan tabel seperti biasa
        table = Table(title=f"Anime Ongoing - Halaman {page}", show_lines=False, box=box.ROUNDED)
        table.add_column("No.", style="cyan", width=5)
        table.add_column("Judul", style="magenta", width=50)
        table.add_column("Episode", style="green", width=10)
        table.add_column("Hari Rilis", style="yellow", width=15)
        
        for idx, anime in enumerate(anime_list, 1):
            table.add_row(str(idx), anime['title'], anime['eps'], anime['hari'])
        console.print(table)
        
        # Menu dengan arrow keys
        menu_options = ["Pilih Anime", "Halaman Selanjutnya", "Halaman Sebelumnya", "Kembali"]
        choice = display_menu_with_arrows(menu_options, "Menu Ongoing")
        
        if choice == 1:
            anime_idx = display_list_with_arrows(
                anime_list, 
                "Pilih Anime", 
                lambda x: f"{x['title']} - {x['eps']}"
            )
            if anime_idx >= 0:
                selected_anime = anime_list[anime_idx]
                handle_anime_details(selected_anime['url'])
        elif choice == 2:
            page += 1
        elif choice == 3:
            page = max(1, page - 1)
        elif choice == 4:
            break
def handle_complete_anime():
    page = 1
    while True:
        with console.status(f"Mengambil anime Complete - Halaman {page}..."):
            anime_list = get_all_complete_anime(page)
        
        if not anime_list:
            console.print("[yellow]Tidak ada lagi anime di halaman berikutnya.[/yellow]")
            page = max(1, page - 1)
            continue

        # Tampilkan tabel seperti biasa
        table = Table(title=f"Anime Ongoing - Halaman {page}", show_lines=False, box=box.ROUNDED)
        table.add_column("No.", style="cyan", width=5)
        table.add_column("Judul", style="magenta", width=50)
        table.add_column("Episode", style="green", width=10)
        table.add_column("Tanggal Rilis", style="yellow", width=15)
        table.add_column("Rating", style="cyan", width= 6)
        
        for idx, anime in enumerate(anime_list, 1):
            table.add_row(str(idx), anime['title'], anime['eps'], anime['hari'], anime['rating'])
        console.print(table)
        
        # Menu dengan arrow keys
        menu_options = ["Pilih Anime", "Halaman Selanjutnya", "Halaman Sebelumnya", "Kembali"]
        choice = display_menu_with_arrows(menu_options, "Menu Complete")
        
        if choice == 1:
            anime_idx = display_list_with_arrows(
                anime_list, 
               "Pilih Anime", 
                lambda x: f"{x['title']} - {x['eps']}"
            )
            if anime_idx >= 0:
                selected_anime = anime_list[anime_idx]
                handle_anime_details(selected_anime['url'])
        elif choice == 2:
            page += 1
        elif choice == 3:
            page = max(1, page - 1)
        elif choice == 4:
            break
            
            
            
def handle_anime_details(url: str):
    console.clear()
    """Menampilkan detail anime dan daftar episode dengan arrow keys"""
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
        # Tampilkan daftar episode dalam tabel
        table = Table(title=f"Daftar Episode (Total: {len(episodes)})", show_lines=True, box=box.ROUNDED)
        table.add_column("No.", style="cyan", width=5)
        table.add_column("Judul Episode", style="magenta")
        table.add_column("Tanggal Rilis", style="green", width=15)

        for idx, ep in enumerate(episodes, 1):
            table.add_row(str(idx), ep['title'], ep['date'])
        console.print(table)

        # Menu dinamis dengan arrow keys
        bookmarks = get_bookmarks()
        is_bookmarked = anime_info['title'] in bookmarks
        
        menu_options = ["Pilih Episode"]
        if is_bookmarked:
            menu_options.append("Hapus Bookmark Ini")
        else:
            menu_options.append("Bookmark Anime Ini")
        menu_options.append("Kembali")

        choice = display_menu_with_arrows(menu_options, "Menu Detail Anime")
        action = menu_options[choice - 1]

        if action == "Pilih Episode":
            ep_idx = display_list_with_arrows(
                episodes,
                "Pilih Episode",
                lambda x: f"{x['title']} - {x['date']}"
            )
            if ep_idx >= 0:
                handle_episode_play(anime_info, episodes, ep_idx)
        
        elif action == "Bookmark Anime Ini":
            save_bookmark(anime_info)
            console.print(f"[bold green]'{anime_info['title']}' berhasil di-bookmark.[/bold green]")
            break
        
        elif action == "Hapus Bookmark Ini":
            delete_bookmark(anime_info['title'])
            console.print(f"[bold yellow]'{anime_info['title']}' telah dihapus dari bookmark.[/bold yellow]")
            break

        elif action == "Kembali":
            break

def handle_episode_play(anime_info: dict, all_episodes: list, current_index: int):
    while True:
        console.clear()
        if not (0 <= current_index < len(all_episodes)):
            console.print("[red]Indeks episode tidak valid.[/red]")
            break

        episode_info = all_episodes[current_index]
        console.clear()
        console.print(Panel(f"Mempersiapkan: [bold cyan]{episode_info['title']}[/bold cyan]", border_style="green"))

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
            quality_idx = display_list_with_arrows(
                qualities,
                "Pilih Kualitas Video",
                lambda x: x
            )
            if quality_idx >= 0:
                final_stream_url = download_links[qualities[quality_idx]]
            else:
                break

        if final_stream_url:
            # Putar video
            playback_successful = stream_anime(final_stream_url)
            
            if playback_successful:
                save_history(anime_info, episode_info)
                console.print(f"[bold blue]Riwayat tontonan untuk '{episode_info['title']}' telah disimpan.[/bold blue]")

        # Menu navigasi setelah menonton
        console.print()
        post_watch_options = []
        if current_index < len(all_episodes) - 1:
            post_watch_options.append("Putar Episode Selanjutnya")
        if current_index > 0:
            post_watch_options.append("Putar Episode Sebelumnya")
        post_watch_options.extend(["Lihat Semua Episode", "Kembali ke Menu Utama"])
        
        choice = display_menu_with_arrows(post_watch_options, "Selesai Menonton")
        action = post_watch_options[choice - 1]
        
        if action == "Putar Episode Selanjutnya":
            current_index += 1
            continue
        elif action == "Putar Episode Sebelumnya":
            current_index -= 1
            continue
        else:
            break

def handle_bookmarks():
    """Menampilkan dan mengelola bookmark dengan arrow keys"""
    while True:
        console.clear(),
        bookmarks = get_bookmarks()
        if not bookmarks:
            console.print("[yellow]Anda belum memiliki bookmark.[/yellow]")
            return
        
        bookmark_list = list(bookmarks.items())
        
        # Tampilkan dalam tabel
        table = Table(title="Daftar Bookmark", show_lines=False, box=box.ROUNDED)
        table.add_column("No.", style="cyan", width=5)
        table.add_column("Judul", style="magenta")
        for i, (title, _) in enumerate(bookmark_list, 1):
            table.add_row(str(i), title)
        console.print(table)
        
        menu_options = ["Lihat Detail", "Hapus Bookmark", "Kembali"]
        choice = display_menu_with_arrows(menu_options, "Menu Bookmark")

        if choice == 1:
            bm_idx = display_list_with_arrows(
                bookmark_list,
                "Pilih Bookmark",
                lambda x: x[0]
            )
            if bm_idx >= 0:
                selected_bm_url = bookmark_list[bm_idx][1]['url']
                handle_anime_details(selected_bm_url)
        elif choice == 2:
            bm_idx = display_list_with_arrows(
                bookmark_list,
                "Hapus Bookmark",
                lambda x: x[0]
            )
            if bm_idx >= 0:
                title_to_delete = bookmark_list[bm_idx][0]
                if delete_bookmark(title_to_delete):
                    console.print(f"[bold green]'{title_to_delete}' berhasil dihapus.[/bold green]")
        elif choice == 3:
            break

def handle_history():
    """Menampilkan riwayat tontonan dengan arrow keys"""
    history = get_history()
    if not history:
        console.print("[yellow]Riwayat tontonan kosong.[/yellow]")
        return
    
    history_list = list(history.items())
    
    table = Table(title="Riwayat Tontonan (Terbaru)", show_lines=True, box=box.ROUNDED)
    table.add_column("No.", style="cyan", width=5)
    table.add_column("Judul Anime", style="magenta")
    table.add_column("Episode Terakhir Ditonton", style="green")
    
    for i, (title, data) in enumerate(history_list, 1):
        table.add_row(str(i), title, data.get('episode_title', 'N/A'))
    console.print(table)

    menu_options = ["Lanjutkan Menonton", "Kembali"]
    choice = display_menu_with_arrows(menu_options, "Pilihan Riwayat")

    if choice == 1:
        history_idx = display_list_with_arrows(
            history_list,
            "Pilih Anime untuk Dilanjutkan",
            lambda x: f"{x[0]} - {x[1].get('episode_title', 'N/A')}"
        )
        if history_idx >= 0:
            _, selected_data = history_list[history_idx]
            
            anime_url = selected_data.get('anime_url')
            last_episode_url = selected_data.get('episode_url')

            if not anime_url or not last_episode_url:
                console.print("[red]Data riwayat tidak lengkap untuk melanjutkan.[/red]")
                return

            with console.status("Mencari episode terakhir ditonton..."):
                anime_info = get_anime_details(anime_url)
                all_episodes = anime_info.get('episodes', [])
                
                last_watched_index = -1
                for i, ep in enumerate(all_episodes):
                    if ep['url'] == last_episode_url:
                        last_watched_index = i
                        break
                
            if last_watched_index != -1:
                console.print(f"[green]Ditemukan! Melanjutkan dari '{all_episodes[last_watched_index]['title']}'...[/green]")
                handle_episode_play(anime_info, all_episodes, last_watched_index)
            else:
                console.print("[red]Tidak dapat menemukan episode terakhir yang ditonton di daftar episode saat ini.[/red]")

def handle_settings():
    """Menu pengaturan dengan arrow keys"""
    settings_menu = [
        "Video Quality",
        "Stream Links", 
        "Change Url Main",
        "Os mode options",
        "Kembali"
    ]
    
    settings = get_settings()
    
    while True:
        console.clear()
        console.print(Panel("[bold cyan]Settings Page[/bold cyan]", style="bold blue"))
        choice = display_menu_with_arrows(settings_menu, "SETTINGS")
        
        console.clear()
        if choice == 1:
            list_quality = ["360p", "480p", "720p"]
            console.print(Panel(f"Quality default saat ini: '{settings.get('default_quality', 'Belum diatur')}'"))
            
            quality_idx = display_list_with_arrows(list_quality, "Available Quality")
            if quality_idx >= 0:
                quality = list_quality[quality_idx]
                set_setting("default_quality", quality)
                console.print(f"[green]Quality default berhasil diubah menjadi '{quality}'[/green]")
            else:
                console.print("[yellow]Tidak ada perubahan pada quality default.[/yellow]")
            
            wait_for_enter()
        elif choice == 2:
            console.print(Panel("[yellow]Fitur ini sedang dalam pengembangan[/yellow]"))
            wait_for_enter()
        elif choice == 3:
            console.print(Panel("Change Url Main"))
            console.print(Panel(f"Domain only: '{settings.get('host_url')}'"))
            choice_url = Prompt.ask("[green]Masukan Url Main[/green]")
            if choice_url:
                console.print(f"[green]Url akan diubah menjadi '{choice_url}'[/green]")
                domain = f"https://{choice_url}"
                set_setting("host_url", domain)
            else:
                console.print("[red]Tidak ada yang diinput. Host url default tetap digunakan.[/red]")
            wait_for_enter()
        elif choice == 4:
            list_mode = ["andorid", "linux", "win"]
            console.print(Panel(f"Quality default saat ini: '{settings.get('options_mode', 'Belum diatur')}'"))
            
            mode_idx = display_list_with_arrows(list_mode, "Available mode")
            if mode_idx >= 0:
                mode = list_mode[mode_idx]
                set_setting("options_mode", mode)
                console.print(f"[green]Quality default berhasil diubah menjadi '{mode}'[/green]")
            else:
                console.print("[yellow]Tidak ada perubahan pada quality default.[/yellow]")
            
            wait_for_enter()
        elif choice == 5:
            break

@app.command(name="start")
def main_cli():
    """Memulai antarmuka CLI interaktif dengan arrow keys"""
    main_menu = [
        "Cari Anime",
        "Ongoing Anime",
        "Complete Anime", 
        "Bookmark",
        "Riwayat Tontonan",
        "Pengaturan",
        "Keluar"
    ]
    
    while True:
        console.clear()
        console.print(Panel("[bold cyan]Selamat Datang di Anime-CLI[/bold cyan]", style="bold blue"))
        choice = display_menu_with_arrows(main_menu, "Menu Utama")
        
        console.clear()
        if choice == 1:
            query = Prompt.ask("[green]Masukkan judul anime[/green]")
            with console.status(f"Mencari '{query}'..."):
                results = search_anime(query)
            
            if not results:
                console.print(f"[red]Tidak ada hasil ditemukan untuk '{query}'.[/red]")
            else:
                table = Table(title=f"Hasil Pencarian untuk '{query}'", show_lines=False, box=box.ROUNDED)
                table.add_column("No.", style="cyan", width=5)
                table.add_column("Judul", style="magenta")
                for idx, anime in enumerate(results, 1):
                    table.add_row(str(idx), anime['title'])
                console.print(table)

                anime_idx = display_list_with_arrows(
                    results,
                    "Pilih Anime",
                    lambda x: x['title']
                )
                if anime_idx >= 0:
                    handle_anime_details(results[anime_idx]['url'])
        
        elif choice == 2:
            handle_ongoing_anime()
        elif choice == 3:
            handle_complete_anime()
        elif choice == 4:
            handle_bookmarks()
        elif choice == 5:
            handle_history()
        elif choice == 6:
            handle_settings()
        elif choice == 7:
            console.print("[bold cyan]Terima kasih! Sampai jumpa![/bold cyan]")
            sys.exit(0)
            
        wait_for_enter()

if __name__ == "__main__":
    app()
