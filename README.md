# YouTube Media Downloader

Este repositório contém um script Python para baixar mídias do YouTube, utilizando a biblioteca `yt-dlp` em conjunto com `ffmpeg`. Ele oferece uma interface gráfica simples usando o `Tkinter` para facilitar o uso.

## Recursos

- Baixa vídeos do YouTube no formato MP4.
- Extrai áudio de vídeos do YouTube no formato MP3.
- Suporta download de playlists inteiras.

## Requisitos

Antes de executar o script, certifique-se de ter o seguinte instalado no seu sistema:

1. Python 3.x: [Download Python](https://www.python.org/downloads/)
2. yt-dlp: Pode ser instalado com o comando `pip install yt-dlp`.
3. FFmpeg: Baixe e instale a partir de [FFmpeg Downloads](https://ffmpeg.org/download.html). Certifique-se de que o caminho do FFmpeg está correto no script (`C:\ffmpeg\bin\ffmpeg.exe`).

## Como executar

Siga os passos abaixo para executar a aplicação:

1. Clone este repositório em sua máquina:
   ```bash
   git clone https://github.com/seu-usuario/nome-do-repositorio.git
   cd nome-do-repositorio
   ```

2. Instale as dependências necessárias:
   ```bash
   pip install yt-dlp
   ```

3. Verifique se o FFmpeg está instalado e o caminho está correto no script.

4. Execute o script:
   ```bash
   python nome_do_script.py
   ```

## Como usar

1. Após iniciar a aplicação, insira a URL da playlist do YouTube ou URLs individuais separadas por vírgula.
2. Selecione o formato desejado (MP4 ou MP3).
3. Clique no botão "Download" para iniciar o processo.
4. Os arquivos baixados serão salvos na área de trabalho, dentro das pastas "vídeos" ou "músicas" conforme o formato escolhido.

## Estrutura do Projeto

```
├── nome_do_script.py   # Script principal
└── README.md           # Documentação
```

## Contribuição

Contribuições são bem-vindas! Por favor, abra uma issue ou envie um pull request para discutir quaisquer alterações que você gostaria de fazer.
