# YouTube Media Downloader

Este repositório contém um script Python para baixar mídias do YouTube, utilizando a biblioteca `yt-dlp` em conjunto com `ffmpeg`. Ele oferece uma interface gráfica simples usando o `Tkinter` para facilitar o uso.

## Recursos

- Baixa vídeos do YouTube nos formatos MP4 e MKV.
- Extrai áudio de vídeos do YouTube nos formatos MP3 e WAV.
- Suporta download de playlists inteiras.
- Permite a escolha da qualidade do vídeo e do áudio.
- Exibe o progresso do download em tempo real.

## Requisitos

Antes de executar o script, certifique-se de ter o seguinte instalado no seu sistema:

1. **Python 3.x**: [Download Python](https://www.python.org/downloads/)
2. **yt-dlp**: Pode ser instalado com o comando:
   ```bash
   pip install yt-dlp
   ```
3. **FFmpeg**: Baixe e instale a partir de [FFmpeg Downloads](https://ffmpeg.org/download.html). Certifique-se de que o caminho do FFmpeg está configurado corretamente no sistema.

## Como executar

Siga os passos abaixo para executar a aplicação:

1. Clone este repositório em sua máquina:
   ```bash
   git clone https://github.com/lsouza-dev/yt-downloader.git
   cd yt-downloader
   ```

2. Instale as dependências necessárias:
   ```bash
   pip install -r requirements.txt
   ```

3. Verifique se o FFmpeg está instalado e o caminho está configurado corretamente no sistema.

4. Execute o script:
   ```bash
   python main.py
   ```

## Como usar

1. Após iniciar a aplicação, insira a URL da playlist do YouTube ou URLs individuais separadas por vírgula.
2. Selecione o formato desejado (MP4, MKV, MP3 ou WAV).
3. Escolha a qualidade preferida para o download.
4. Clique no botão "Download" para iniciar o processo.
5. Os arquivos baixados serão salvos na pasta "Downloads" do seu usuário, dentro das subpastas "Vídeos" ou "Músicas", conforme o formato escolhido.

## Estrutura do Projeto

```
├── main.py             # Script principal
└── README.md           # Documentação
```

## Contribuição

Contribuições são bem-vindas! Por favor, abra uma issue ou envie um pull request para discutir quaisquer alterações que você gostaria de fazer.

