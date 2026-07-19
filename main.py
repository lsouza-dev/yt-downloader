import os
import subprocess
import sys
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

# Cache para FFmpeg validation
_ffmpeg_cache = {"checked": False, "valid": False, "path": None}

def validate_ffmpeg():
    if _ffmpeg_cache["checked"]:
        return _ffmpeg_cache["valid"], _ffmpeg_cache["path"]

    # 1. Tenta achar o FFmpeg instalado globalmente no sistema (Linux/Mac/Windows no PATH)
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        ffmpeg_dir = str(Path(system_ffmpeg).parent)
        _ffmpeg_cache["checked"] = True
        _ffmpeg_cache["valid"] = True
        _ffmpeg_cache["path"] = ffmpeg_dir
        return True, ffmpeg_dir

    # 2. Fallback: Procura na pasta local (antigo padrão do Windows)
    base_dir = Path(__file__).resolve().parent
    ffmpeg_exe = base_dir / "ffmpeg" / "bin" / "ffmpeg.exe"

    is_valid = ffmpeg_exe.is_file()
    ffmpeg_dir = ffmpeg_exe.parent if is_valid else None

    _ffmpeg_cache["checked"] = True
    _ffmpeg_cache["valid"] = is_valid
    _ffmpeg_cache["path"] = str(ffmpeg_dir) if is_valid else None

    return is_valid, str(ffmpeg_dir) if ffmpeg_dir else None 

def detect_js_runtime():
    """Retorna o runtime JavaScript mais adequado disponível no sistema."""
    for runtime in ("node", "deno"):
        if shutil.which(runtime):
            return runtime
    return None


def build_download_command(url, media_type, quality, download_path, ffmpeg_path):
    """Constrói o comando yt-dlp otimizado, sem restrições de cliente e forçando sobrescrita."""
    js_runtime = detect_js_runtime()
    base_command = [
        sys.executable, "-m", "yt_dlp",
        "--yes-playlist",
        "--geo-bypass",
        "--ffmpeg-location", ffmpeg_path,
        "-o", os.path.join(download_path, f"%(title)s_{quality}.%(ext)s"),
        "--no-progress",
        "--force-overwrites",
        url,
    ]

    if js_runtime:
        base_command.insert(3, "--js-runtimes")
        base_command.insert(4, js_runtime)

    if "youtube.com" in url or "youtu.be" in url:
        base_command.insert(3, "--extractor-args")
        base_command.insert(4, "youtube:player_client=android")
    
    if media_type == "mp3":
        qual_val = quality.replace("k", "")
        base_command.extend(["-x", "--audio-format", "mp3", "--audio-quality", qual_val])
        
    elif media_type == "mp4":
        if quality == "best":
            # Pega a melhor qualidade de vídeo e áudio separadamente e depois junta
            base_command.extend(["-f", "bestvideo+bestaudio/best"])
        else:
            res = quality.replace("p", "")
            # PADRÃO OFICIAL YT-DLP: Usa o -S (Format Sort) para definir o teto de resolução.
            # Ele vai listar tudo que o YouTube oferece e pegar o melhor vídeo que seja <= res.
            base_command.extend(["-S", f"res:{res}", "-f", "bestvideo+bestaudio/best"])
        
        base_command.extend(["--merge-output-format", "mp4"])
    
    return base_command


def add_download_item():
    """Adiciona um novo link à lista de downloads"""
    url = url_entry.get().strip()
    media_type = download_type.get()
    media_quality = quality_var.get()
    
    if not url:
        messagebox.showwarning("Aviso", "Por favor, insira uma URL.")
        return
    
    if not url.startswith(('http://', 'https://')):
        messagebox.showwarning("Aviso", "A URL deve começar com http:// ou https://")
        return
    
    item_frame = ttk.Frame(downloads_list_frame, relief=tk.FLAT)
    item_frame.pack(fill=tk.X, pady=3)
    
    url_display = url if len(url) <= 50 else url[:47] + "..."
    url_label = ttk.Label(item_frame, text=f"🔗 {url_display}", width=80, anchor=tk.W)
    url_label.pack(side=tk.LEFT, padx=5)
    
    type_display = "🎥 MP4" if media_type == "mp4" else "🔊 MP3"
    type_label = ttk.Label(item_frame, text=type_display, width=15, anchor=tk.W)
    type_label.pack(side=tk.LEFT)
    
    quality_label = ttk.Label(item_frame, text=f"⭐ {media_quality}", width=15, anchor=tk.W)
    quality_label.pack(side=tk.LEFT)
    
    def remove_item():
        item_frame.destroy()
        if item_frame in downloads_data:
            del downloads_data[item_frame]
        update_counter()
        update_scroll_region()
    
    delete_btn = ttk.Button(item_frame, text="❌", command=remove_item, width=10)
    delete_btn.pack(side=tk.LEFT, anchor=tk.CENTER)
    
    downloads_data[item_frame] = {"url": url, "type": media_type, "quality": media_quality, "frame": item_frame}
    
    url_entry.delete(0, tk.END)
    url_entry.focus()
    update_counter()
    update_scroll_region()

def update_counter():
    count = len(downloads_data)
    counter_label.config(text=f"📋 {count} link(s) adicionado(s)")

def update_scroll_region():
    downloads_list_frame.update_idletasks()
    downloads_canvas.config(scrollregion=downloads_canvas.bbox("all"))

def escolher_diretorio():
    pasta = filedialog.askdirectory(title="Selecione a pasta de destino")
    if pasta:
        output_dir_var.set(pasta)

def atualizar_opcoes_qualidade(*args):
    """Muda as opções de qualidade dependendo se é MP3 ou MP4"""
    if download_type.get() == 'mp3':
        quality_combo.config(values=['128k', '192k', '320k'])
        quality_var.set('192k')
    else:
        quality_combo.config(values=['best', '1080p', '720p', '480p'])
        quality_var.set('best')

def start_download():
    """Inicia o download de todos os itens da lista"""
    if not downloads_data:
        messagebox.showwarning("Aviso", "Adicione pelo menos um link antes de fazer download.")
        return
        
    download_dir = output_dir_var.get()
    if not download_dir or not os.path.exists(download_dir):
        messagebox.showwarning("Aviso", "Por favor, selecione uma pasta de destino válida.")
        return
    
    output_box.delete('1.0', tk.END)
    progress_label.config(text="Arquivos baixados: 0 de 0")
    
    download_items = [
        {"url": data["url"], "type": data["type"], "quality": data["quality"]} 
        for data in downloads_data.values()
    ]
    
    download_button.config(state=tk.DISABLED)
    add_button.config(state=tk.DISABLED)
    url_entry.config(state=tk.DISABLED)
    type_combo.config(state=tk.DISABLED)
    quality_combo.config(state=tk.DISABLED)
    dir_btn.config(state=tk.DISABLED)
    
    def download_thread():
        try:
            ffmpeg_valid, ffmpeg_path = validate_ffmpeg()
            if not ffmpeg_valid:
                messagebox.showerror("Erro", "FFmpeg não encontrado no sistema ou na pasta do projeto.")
                return

            total_downloads = len(download_items)
            completed = 0
            
            output_box.insert(tk.END, f"📥 Iniciando {total_downloads} download(s) na pasta: {download_dir}\n\n")
            output_box.update_idletasks()

            for idx, item in enumerate(download_items, 1):
                url = item["url"]
                media_type = item["type"]
                quality = item["quality"]
                
                output_box.insert(tk.END, f"[{idx}/{total_downloads}] Baixando: {url}\n")
                output_box.insert(tk.END, f"Tipo: {media_type.upper()} | Qualidade: {quality}\n")
                output_box.see(tk.END)
                output_box.update_idletasks()
                
                command = build_download_command(url, media_type, quality, download_dir, ffmpeg_path)
                
                env = os.environ.copy()
                if ffmpeg_path:
                    env["PATH"] = ffmpeg_path + os.pathsep + env.get("PATH", "")

                try:
                    process = subprocess.Popen(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1,
                        env=env
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
            quality_combo.config(state=tk.NORMAL)
            dir_btn.config(state=tk.NORMAL)
    
    threading.Thread(target=download_thread, daemon=True).start()

# === Inicialização da Interface ===
root = tk.Tk()
root.title("YouTube Media Downloader")
root.geometry("1000x900")
root.resizable(True, True)

style = ttk.Style()
style.theme_use('clam')

main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

title_label = ttk.Label(main_frame, text="🎬 YouTube Media Downloader", font=("Arial", 18, "bold"))
title_label.pack(pady=5)

# --- DIRETÓRIO SECTION ---
dir_section = ttk.LabelFrame(main_frame, text=" 1. Pasta de Destino ", padding="10")
dir_section.pack(fill=tk.X, pady=5)

output_dir_var = tk.StringVar(value=str(Path.home() / "Downloads"))

dir_entry = ttk.Entry(dir_section, textvariable=output_dir_var, state='readonly')
dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

dir_btn = ttk.Button(dir_section, text="📂 Escolher Pasta...", command=escolher_diretorio)
dir_btn.pack(side=tk.RIGHT, padx=5)

# --- INPUT SECTION ---
input_section = ttk.LabelFrame(main_frame, text=" 2. Adicionar Link ", padding="10")
input_section.pack(fill=tk.X, pady=5)

input_inner = ttk.Frame(input_section)
input_inner.pack(fill=tk.X)

ttk.Label(input_inner, text="URL:").pack(side=tk.LEFT, padx=5)
url_entry = ttk.Entry(input_inner, width=40)
url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
url_entry.bind('<Return>', lambda e: add_download_item())

ttk.Label(input_inner, text="Tipo:").pack(side=tk.LEFT, padx=5)
download_type = tk.StringVar(value='mp4')
type_combo = ttk.Combobox(input_inner, textvariable=download_type, values=['mp4', 'mp3'], width=6, state='readonly')
type_combo.pack(side=tk.LEFT, padx=5)

ttk.Label(input_inner, text="Qualidade:").pack(side=tk.LEFT, padx=5)
quality_var = tk.StringVar(value='best')
quality_combo = ttk.Combobox(input_inner, textvariable=quality_var, values=['best', '1080p', '720p', '480p'], width=8, state='readonly')
quality_combo.pack(side=tk.LEFT, padx=5)

# Evento para atualizar as qualidades quando mudar o tipo
download_type.trace_add('write', atualizar_opcoes_qualidade)

add_button = ttk.Button(input_inner, text="➕ Adicionar", command=add_download_item)
add_button.pack(side=tk.LEFT, padx=10)

# --- TABLE SECTION ---
table_section = ttk.LabelFrame(main_frame, text=" 3. Links na Fila ", padding="5")
table_section.pack(fill=tk.BOTH, expand=True, pady=5)

downloads_canvas = tk.Canvas(table_section, bg="#f0f0f0", highlightthickness=0)
downloads_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(table_section, orient=tk.VERTICAL, command=downloads_canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
downloads_canvas.config(yscrollcommand=scrollbar.set)

downloads_list_frame = ttk.Frame(downloads_canvas)
downloads_canvas.create_window((0, 0), window=downloads_list_frame, anchor=tk.NW)

header_frame = ttk.Frame(downloads_list_frame)
header_frame.pack(fill=tk.X, pady=5, padx=5)
ttk.Label(header_frame, text="🔗 Link", width=80, anchor=tk.W).pack(side=tk.LEFT, padx=5)
ttk.Label(header_frame, text="📝 Tipo", width=15, anchor=tk.W).pack(side=tk.LEFT, padx=5)
ttk.Label(header_frame, text="⭐ Qualidade", width=15, anchor=tk.W).pack(side=tk.LEFT, padx=5)
ttk.Label(header_frame, text="❌ Remover", width=10, anchor=tk.W).pack(side=tk.LEFT, padx=5)

ttk.Separator(downloads_list_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=2)

counter_label = ttk.Label(main_frame, text="📋 0 link(s) adicionado(s)", font=("Arial", 10))
counter_label.pack(pady=2)

# --- OUTPUT SECTION ---
output_frame = ttk.LabelFrame(main_frame, text=" 4. Console de Progresso ", padding="5")
output_frame.pack(fill=tk.BOTH, expand=True, pady=5)

output_box = tk.Text(output_frame, height=10, width=100, wrap=tk.WORD, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 9))
output_box.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

output_scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=output_box.yview)
output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
output_box.config(yscrollcommand=output_scrollbar.set)

# --- BOTTOM SECTION ---
progress_frame = ttk.Frame(main_frame)
progress_frame.pack(fill=tk.X, pady=10)

progress_label = ttk.Label(progress_frame, text="Arquivos baixados: 0 de 0", font=("Arial", 10, "bold"))
progress_label.pack(side=tk.LEFT, padx=5)

download_button = ttk.Button(progress_frame, text="⬇️ Iniciar Download", command=start_download)
download_button.pack(side=tk.RIGHT, padx=5)

downloads_data = {}

root.mainloop()