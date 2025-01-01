import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import threading
import json

def get_download_path(media_type):
    desktop_path = Path.home() / "Desktop"
    if media_type == "mp3":
        return desktop_path / "músicas"
    elif media_type == "mp4":
        return desktop_path / "vídeos"
    return desktop_path

def download_media_with_ytdlp(youtube_urls, media_type, output_box, progress_label, download_button):
    try:
        ffmpeg_path = "C:\\ffmpeg\\bin\\ffmpeg.exe"
        if not os.path.isfile(ffmpeg_path):
            messagebox.showerror("Error", f"FFmpeg não encontrado no caminho especificado: {ffmpeg_path}")
            return

        download_path = get_download_path(media_type)
        os.makedirs(download_path, exist_ok=True)

        successful_downloads = 0

        for url in youtube_urls:
            url = url.strip()
            if not url:
                continue

            # Obter o número de itens na playlist
            command_probe = [
                sys.executable, "-m", "yt_dlp",
                "--flat-playlist", "--dump-json",
                url
            ]

            probe_process = subprocess.Popen(command_probe, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            probe_output, _ = probe_process.communicate()

            entries = []
            if probe_process.returncode == 0:
                entries = [json.loads(entry) for entry in probe_output.splitlines() if entry.strip()]

            command = [
                sys.executable, "-m", "yt_dlp",
                "--yes-playlist",
                "--ffmpeg-location", ffmpeg_path,
                "-o", os.path.join(download_path, "%(playlist_index)s - %(title)s.%(ext)s"),
                url
            ]

            if media_type == "mp3":
                command.insert(4, "-x")
                command.insert(5, "--audio-format")
                command.insert(6, "mp3")
            elif media_type == "mp4":
                command.extend(["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio"])
                command.extend(["--merge-output-format", "mp4"])

            output_box.insert(tk.END, f"Iniciando downloads para: {url}\n")
            output_box.update_idletasks()

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

            for line in process.stdout:
                output_box.insert(tk.END, line)
                output_box.see(tk.END)
                output_box.update_idletasks()

                # Verifica se a linha corresponde à conclusão de um download no formato desejado
                if "Destination:" in line and (line.endswith('.mp4\n') or line.endswith('.mp3\n')):
                    successful_downloads += 1
                    progress_label.config(text=f"Arquivos baixados: {successful_downloads} de {len(entries)}")
                    progress_label.update_idletasks()

            process.stdout.close()
            process.wait()

            if process.returncode != 0:
                output_box.insert(tk.END, f"Erro ao baixar de: {url}\n")
                output_box.insert(tk.END, process.stderr.read())
                output_box.see(tk.END)
                process.stderr.close()

    except Exception as e:
        output_box.insert(tk.END, f"Ocorreu um erro: {e}\n")
        output_box.update_idletasks()

    finally:
        download_button.config(state=tk.NORMAL)

def start_download():
    output_box.delete('1.0', tk.END)
    progress_label.config(text="Arquivos baixados: 0 de 0")
    urls_input = url_entry.get().strip()
    media_type = download_type.get()
    if urls_input:
        youtube_urls = [url.strip() for url in urls_input.split(',') if url.strip()]
        if youtube_urls:
            download_button.config(state=tk.DISABLED)
            threading.Thread(target=download_media_with_ytdlp, args=(youtube_urls, media_type, output_box, progress_label, download_button), daemon=True).start()
        else:
            messagebox.showwarning("Input Error", "Por favor, insira URLs válidas.")
    else:
        messagebox.showwarning("Input Error", "Por favor, insira todos os campos necessários.")

# Interface Tkinter
root = tk.Tk()
root.title("YouTube Media Downloader")

root.geometry("600x550")

frame = ttk.Frame(root)
frame.place(relx=0.5, rely=0.4, anchor='center')

url_label = ttk.Label(frame, text="Insira a URL da playlist ou as URLs individuais separadas por vírgula:")
url_label.pack(pady=5)
url_entry = ttk.Entry(frame, width=50)
url_entry.pack(pady=5)

download_type_label = ttk.Label(frame, text="Selecione o tipo de download:")
download_type_label.pack(pady=5)
download_type = tk.StringVar(value='mp3')
mp4_radio = ttk.Radiobutton(frame, text='MP4', variable=download_type, value='mp4')
mp4_radio.pack()
mp3_radio = ttk.Radiobutton(frame, text='MP3 (Audio Only)', variable=download_type, value='mp3')
mp3_radio.pack()

download_button = ttk.Button(frame, text="Download", command=start_download)
download_button.pack(pady=20)

output_box = tk.Text(frame, height=10, width=70)
output_box.pack(pady=5)

progress_label = ttk.Label(frame, text="Arquivos baixados: 0 de 0")
progress_label.pack(pady=5)

root.mainloop()