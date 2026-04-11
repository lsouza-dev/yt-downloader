import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

# Cache para FFmpeg validation
_ffmpeg_cache = {"checked": False, "valid": False, "path": None}

def get_download_path(media_type):
    desktop_path = Path.home() / "Desktop"
    if media_type == "mp3":
        return desktop_path / "músicas"
    elif media_type == "mp4":
        return desktop_path / "vídeos"
    return desktop_path

def validate_ffmpeg():
    if _ffmpeg_cache["checked"]:
        return _ffmpeg_cache["valid"], _ffmpeg_cache["path"]

    base_dir = Path(__file__).resolve().parent
    ffmpeg_exe = base_dir / "ffmpeg" / "bin" / "ffmpeg.exe"

    is_valid = ffmpeg_exe.is_file()

    # 🔥 aqui está a mudança: pegar a PASTA
    ffmpeg_dir = ffmpeg_exe.parent if is_valid else None

    _ffmpeg_cache["checked"] = True
    _ffmpeg_cache["valid"] = is_valid
    _ffmpeg_cache["path"] = str(ffmpeg_dir) if is_valid else None

    return is_valid, str(ffmpeg_dir) if ffmpeg_dir else None 

def build_download_command(url, media_type, download_path, ffmpeg_path):
    """Constrói o comando yt-dlp otimizado"""
    base_command = [
        sys.executable, "-m", "yt_dlp",
        "--yes-playlist",
        "--geo-bypass",
        "--age-limit", "99",
        "--extractor-args", "youtube:player_client=android",  # Change to android
        "--js-runtimes", "node",
        "--ffmpeg-location", ffmpeg_path,
        "-o", os.path.join(download_path,"%(title)s.%(ext)s"),
        "--no-warnings",
        "-q",
        url
    ]
    
    if media_type == "mp3":
        base_command.extend(["-x", "--audio-format", "mp3", "--audio-quality", "192"])
    elif media_type == "mp4":
        base_command.extend(["-f", "best"])
        base_command.extend(["--merge-output-format", "mp4"])
    
    return base_command

def download_single_url(url, media_type, download_path, ffmpeg_path, output_queue):
    """Download de um URL individual"""
    try:
        url = url.strip()
        if not url:
            return {"status": "skipped", "url": url, "message": "URL vazia"}
        
        command = build_download_command(url, media_type, download_path, ffmpeg_path)
        env = os.environ.copy()
        env["PATH"] = ffmpeg_path + os.pathsep + env["PATH"]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env  # 🔥 aqui está a mágica
        )
        
        output_lines = []
        for line in process.stdout:
            output_lines.append(line)
            output_queue.put(("log", line))
        
        process.wait()
        
        if process.returncode == 0:
            return {"status": "success", "url": url, "lines": len(output_lines)}
        else:
            return {"status": "error", "url": url, "message": "yt-dlp retornou código de erro"}
            
    except Exception as e:
        return {"status": "error", "url": url, "message": str(e)}

def download_media_with_ytdlp(youtube_urls, media_type, output_box, progress_label, download_button):
    """Download otimizado com processamento paralelo"""
    try:
        # Validar FFmpeg uma única vez
        ffmpeg_valid, ffmpeg_path = validate_ffmpeg()
        if not ffmpeg_valid:
            messagebox.showerror("Error", f"FFmpeg não encontrado no caminho: {ffmpeg_path}")
            return

        download_path = get_download_path(media_type)
        os.makedirs(download_path, exist_ok=True)

        # Filtrar URLs vazias
        urls_validas = [url.strip() for url in youtube_urls if url.strip()]
        if not urls_validas:
            messagebox.showwarning("Input Error", "Nenhuma URL válida fornecida.")
            return

        total_urls = len(urls_validas)
        output_box.insert(tk.END, f"📥 Iniciando {total_urls} download(s) em paralelo...\n")
        output_box.update_idletasks()

        output_queue = queue.Queue()
        completed_count = 0

        # Usar ThreadPoolExecutor para downloads paralelos (máx 3 simultâneos)
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(download_single_url, url, media_type, download_path, ffmpeg_path, output_queue): url
                for url in urls_validas
            }

            # Processar outputs da fila enquanto aguarda conclusão
            def process_queue():
                nonlocal completed_count
                while futures:
                    try:
                        msg_type, content = output_queue.get(timeout=0.1)
                        if msg_type == "log":
                            output_box.insert(tk.END, content)
                            output_box.see(tk.END)
                            output_box.update_idletasks()
                    except queue.Empty:
                        pass

                    # Verificar se alguma task completou
                    done, futures = {f: futures[f] for f in futures if f.done()}, {f: futures[f] for f in futures if not f.done()}
                    for future in done:
                        completed_count += 1
                        result = future.result()
                        status_icon = "✅" if result["status"] == "success" else "❌"
                        output_box.insert(tk.END, f"{status_icon} [{completed_count}/{total_urls}] {result['url']}\n")
                        progress_label.config(text=f"Arquivos baixados: {completed_count} de {total_urls}")
                        output_box.see(tk.END)
                        output_box.update_idletasks()

            # Aguardar todas as tasks
            for future in as_completed(futures):
                process_queue()

            # Processa último batch da fila
            process_queue()

        output_box.insert(tk.END, "\n✨ Download concluído!\n")
        output_box.update_idletasks()

    except Exception as e:
        output_box.insert(tk.END, f"❌ Erro: {e}\n")
        output_box.update_idletasks()

    finally:
        download_button.config(state=tk.NORMAL)

def add_download_item():
    """Adiciona um novo link à lista de downloads"""
    url = url_entry.get().strip()
    media_type = download_type.get()
    
    if not url:
        messagebox.showwarning("Input Error", "Por favor, insira uma URL.")
        return
    
    if not url.startswith(('http://', 'https://')):
        messagebox.showwarning("Input Error", "URL deve começar com http:// ou https://")
        return
    
    # Criar um novo frame para a linha
    item_frame = ttk.Frame(downloads_list_frame, relief=tk.FLAT)
    item_frame.pack(fill=tk.X, pady=3)
    
    # Label com a URL (truncada para exibição)
    url_display = url if len(url) <= 60 else url[:57] + "..."
    url_label = ttk.Label(item_frame, text=f"🔗 {url_display}", width=117, anchor=tk.W)
    url_label.pack(side=tk.LEFT, padx=5)
    
    # Label com o tipo
    type_display = "🎥 MP4" if media_type == "mp4" else "🔊 MP3"
    type_label = ttk.Label(item_frame, text=type_display, width=20, anchor=tk.W)
    type_label.pack(side=tk.LEFT)
    
    # Botão de remover
    def remove_item():
        item_frame.destroy()
        if item_frame in downloads_data:
            del downloads_data[item_frame]
        update_counter()
        update_scroll_region()
    
    delete_btn = ttk.Button(item_frame, text="❌", command=remove_item, width=15)
    delete_btn.pack(side=tk.LEFT,anchor=tk.CENTER)
    
    # Armazenar dados
    downloads_data[item_frame] = {"url": url, "type": media_type, "frame": item_frame}
    
    # Limpar entrada
    url_entry.delete(0, tk.END)
    url_entry.focus()
    
    # Atualizar
    update_counter()
    update_scroll_region()

def delete_download_item():
    """Remove todos os itens (mantido por compatibilidade)"""
    pass

def update_counter():
    """Atualiza o contador de links"""
    count = len(downloads_data)
    counter_label.config(text=f"📋 {count} link(s) adicionado(s)")

def update_scroll_region():
    """Atualiza a região de scroll do canvas"""
    downloads_list_frame.update_idletasks()
    downloads_canvas.config(scrollregion=downloads_canvas.bbox("all"))

def start_download():
    """Inicia o download de todos os itens da lista"""
    if not downloads_data:
        messagebox.showwarning("Input Error", "Adicione pelo menos um link antes de fazer download.")
        return
    
    output_box.delete('1.0', tk.END)
    progress_label.config(text="Arquivos baixados: 0 de 0")
    
    # Preparar lista de URLs com seus tipos
    download_items = [
        {"url": data["url"], "type": data["type"]} 
        for data in downloads_data.values()
    ]
    
    download_button.config(state=tk.DISABLED)
    add_button.config(state=tk.DISABLED)
    url_entry.config(state=tk.DISABLED)
    type_combo.config(state=tk.DISABLED)
    
    # Usar thread para não congelar a interface
    def download_thread():
        try:
            # Validar FFmpeg uma única vez
            ffmpeg_valid, ffmpeg_path = validate_ffmpeg()
            if not ffmpeg_valid:
                messagebox.showerror("Error", f"FFmpeg não encontrado: {ffmpeg_path}")
                return

            total_downloads = len(download_items)
            completed = 0
            
            output_box.insert(tk.END, f"📥 Iniciando {total_downloads} download(s)...\n\n")
            output_box.update_idletasks()

            # Processar cada tipo de download separadamente para melhor controle
            for idx, item in enumerate(download_items, 1):
                url = item["url"]
                media_type = item["type"]
                
                download_path = get_download_path(media_type)
                os.makedirs(download_path, exist_ok=True)
                
                output_box.insert(tk.END, f"[{idx}/{total_downloads}] Baixando: {url}\n")
                output_box.insert(tk.END, f"Tipo: {'🎥 MP4' if media_type == 'mp4' else '🔊 MP3'}\n")
                output_box.see(tk.END)
                output_box.update_idletasks()
                
                command = build_download_command(url, media_type, download_path, ffmpeg_path)
                
                try:
                    process = subprocess.Popen(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1
                    )
                    
                    for line in process.stdout:
                        output_box.insert(tk.END, line)
                        output_box.see(tk.END)
                        output_box.update_idletasks()
                    
                    process.wait()
                    
                    if process.returncode == 0:
                        completed += 1
                        output_box.insert(tk.END, f"✅ Download concluído!\n\n")
                    else:
                        output_box.insert(tk.END, f"❌ Erro ao baixar este link\n\n")
                    
                    output_box.see(tk.END)
                    progress_label.config(text=f"Arquivos baixados: {completed} de {total_downloads}")
                    output_box.update_idletasks()
                    
                except Exception as e:
                    output_box.insert(tk.END, f"❌ Erro: {str(e)}\n\n")
                    output_box.see(tk.END)
                    output_box.update_idletasks()
            
            output_box.insert(tk.END, "\n✨ Todos os downloads foram processados!\n")
            output_box.see(tk.END)
            output_box.update_idletasks()
            
        except Exception as e:
            output_box.insert(tk.END, f"❌ Erro geral: {str(e)}\n")
            output_box.update_idletasks()
        finally:
            download_button.config(state=tk.NORMAL)
            add_button.config(state=tk.NORMAL)
            url_entry.config(state=tk.NORMAL)
            type_combo.config(state=tk.NORMAL)
    
    threading.Thread(target=download_thread, daemon=True).start()

# Interface Tkinter
root = tk.Tk()
root.title("YouTube Media Downloader")
root.geometry("1000x900")
root.resizable(True, True)

# Estilos
style = ttk.Style()
style.theme_use('clam')

# Frame principal
main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

# Título
title_label = ttk.Label(main_frame, text="🎬 YouTube Media Downloader", font=("Arial", 18, "bold"))
title_label.pack(pady=5)

# ===== INPUT SECTION =====
input_section = ttk.LabelFrame(main_frame, text="Adicionar Link", padding="10")
input_section.pack(fill=tk.X, pady=5)

input_inner = ttk.Frame(input_section)
input_inner.pack(fill=tk.X)

url_label = ttk.Label(input_inner, text="URL:")
url_label.pack(side=tk.LEFT, padx=5)

url_entry = ttk.Entry(input_inner, width=50)
url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
url_entry.bind('<Return>', lambda e: add_download_item())  # Enter para adicionar

type_label = ttk.Label(input_inner, text="Tipo:")
type_label.pack(side=tk.LEFT, padx=5)

download_type = tk.StringVar(value='mp3')
type_combo = ttk.Combobox(input_inner, textvariable=download_type, values=['mp4', 'mp3'], width=6, state='readonly')
type_combo.pack(side=tk.LEFT, padx=5)

add_button = ttk.Button(input_inner, text="➕ Adicionar", command=add_download_item)
add_button.pack(side=tk.LEFT, padx=5)

# ===== DOWNLOADS LIST SECTION (Com Canvas + Scroll) =====
table_section = ttk.LabelFrame(main_frame, text="Links para Download", padding="5")
table_section.pack(fill=tk.BOTH, expand=True, pady=5)

# Canvas com scrollbar (sem height fixa)
downloads_canvas = tk.Canvas(table_section, bg="#f0f0f0", highlightthickness=0)
downloads_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(table_section, orient=tk.VERTICAL, command=downloads_canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
downloads_canvas.config(yscrollcommand=scrollbar.set)

# Frame dentro do canvas
downloads_list_frame = ttk.Frame(downloads_canvas)
downloads_canvas.create_window((0, 0), window=downloads_list_frame, anchor=tk.NW)

# Cabeçalho da tabela
header_frame = ttk.Frame(downloads_list_frame)
header_frame.pack(fill=tk.X, pady=5, padx=5)
ttk.Label(header_frame, text="🔗 Link", width=115, anchor=tk.W).pack(side=tk.LEFT, padx=5)
ttk.Label(header_frame, text="📝 Tipo", width=20, anchor=tk.W).pack(side=tk.LEFT, padx=5)
ttk.Label(header_frame, text="❌ Remover", width=15, anchor=tk.W).pack(side=tk.LEFT, padx=5)

# Separador
ttk.Separator(downloads_list_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=2)

# Counter
counter_label = ttk.Label(main_frame, text="📋 0 link(s) adicionado(s)", font=("Arial", 10))
counter_label.pack(pady=2)

# ===== OUTPUT SECTION =====
output_frame = ttk.LabelFrame(main_frame, text="📊 Log de Download", padding="5")
output_frame.pack(fill=tk.BOTH, expand=True, pady=5)

output_box = tk.Text(output_frame, height=8, width=100, wrap=tk.WORD, bg="#f0f0f0")
output_box.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

output_scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=output_box.yview)
output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
output_box.config(yscrollcommand=output_scrollbar.set)

# ===== PROGRESS & DOWNLOAD =====
progress_frame = ttk.Frame(main_frame)
progress_frame.pack(fill=tk.X, pady=5)

progress_label = ttk.Label(progress_frame, text="Arquivos baixados: 0 de 0", font=("Arial", 10))
progress_label.pack(side=tk.LEFT, padx=5)

download_button = ttk.Button(progress_frame, text="⬇️ Iniciar Download", command=start_download)
download_button.pack(side=tk.RIGHT, padx=5)

# Estrutura de dados global para armazenar downloads
downloads_data = {}

root.mainloop()