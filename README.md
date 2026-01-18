# 🎬 YouTube Media Downloader

Uma aplicação desktop moderna e eficiente para baixar vídeos e áudio do YouTube com interface gráfica intuitiva.

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

</div>

---

## ✨ Recursos Principais

- ✅ **Download de Vídeos** em MP4 com melhor qualidade disponível
- ✅ **Extração de Áudio** em MP3 com qualidade 192kbps
- ✅ **Suporte a Playlists** - baixe múltiplos vídeos em uma vez
- ✅ **Downloads Paralelos** - até 3 downloads simultâneos para melhor performance
- ✅ **Interface Gráfica** moderna e amigável com Tkinter
- ✅ **Gerenciamento de Links** - adicione, visualize e remova links facilmente
- ✅ **Log em Tempo Real** - acompanhe o progresso de cada download
- ✅ **Validação de FFmpeg** - cache de validação para melhor performance
- ✅ **Suporte a Windows** com integração ao Desktop

---

## 🚀 Início Rápido

### Pré-requisitos

- **Python** 3.8 ou superior
- **FFmpeg** instalado e configurado

### Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/yt-downloader.git
cd yt-downloader
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Configure o FFmpeg**
   
   **Windows:**
   - Baixe FFmpeg de https://ffmpeg.org/download.html
   - Extraia o arquivo
   - Crie a pasta `C:\ffmpeg\bin\` 
   - Coloque `ffmpeg.exe` dentro dela
   - Ou configure o PATH do sistema

4. **Execute a aplicação**
```bash
python main.py
```

---

## 📖 Como Usar

### Passo a Passo

1. **Abra a aplicação** executando `python main.py`

2. **Adicione um link:**
   - Cole a URL do YouTube no campo "URL"
   - Selecione o tipo (MP3 ou MP4)
   - Clique em "➕ Adicionar" ou pressione Enter

3. **Gerencie seus links:**
   - Veja todos os links adicionados na tabela
   - Clique em "❌" para remover um link individual
   - O contador mostra quantos links estão na fila

4. **Inicie o download:**
   - Clique em "⬇️ Iniciar Download"
   - Acompanhe o progresso no log em tempo real
   - Os arquivos serão salvos em:
     - MP3: `Desktop/músicas`
     - MP4: `Desktop/vídeos`

### Exemplo de URLs Suportadas

- Vídeos individuais: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- Playlists: `https://www.youtube.com/playlist?list=PLxxxxxx`
- Shorts: `https://www.youtube.com/shorts/xxxxx`

---

## ⚙️ Otimizações Implementadas

| Feature | Antes | Depois | Ganho |
|---------|-------|--------|-------|
| Download Múltiplos | Sequencial | Paralelo (3x) | **2-3x mais rápido** |
| Validação FFmpeg | A cada URL | Cache por sessão | **Reduz I/O disco** |
| Seleção de Formato | Genérica | Otimizada | **Melhor qualidade** |
| Output Console | Verboso | Quiet Mode | **Interface limpa** |
| Thread Safety | Não | Queue-based | **Sem deadlocks** |

---

## 🏗️ Estrutura do Projeto

```
yt-downloader/
├── main.py                 # Aplicação principal
├── requirements.txt        # Dependências do projeto
├── README.md              # Esta documentação
└── __pycache__/           # Cache Python
```

---

## 📦 Dependências

```
yt-dlp>=2024.1.0          # Download do YouTube
```

Tkinter vem pré-instalado com Python no Windows.

---

## 🎯 Especificações Técnicas

### Configurações de Download

**MP4 (Vídeo):**
- Formato: `bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]`
- Merge: MP4
- Máxima qualidade disponível

**MP3 (Áudio):**
- Formato: MP3
- Qualidade: 192kbps
- Perfeito para música

### Performance

- **Workers Paralelos:** 3 downloads simultâneos
- **Timeout de Fila:** 0.1 segundos
- **Atualização UI:** Em tempo real
- **Cache FFmpeg:** Por sessão

---

## 🐛 Solução de Problemas

### FFmpeg não encontrado
```
❌ Erro: FFmpeg não encontrado no caminho: C:\ffmpeg\bin\ffmpeg.exe
```
**Solução:** Instale FFmpeg em `C:\ffmpeg\bin\` ou configure o PATH do sistema.

### Erro "URL vazia"
Certifique-se de que a URL começa com `http://` ou `https://`

### Download muito lento
- Verifique sua conexão com internet
- Tente com um vídeo de menor duração
- Múltiplos downloads paralelos podem consumir banda

---

## 💡 Dicas de Uso

- ✓ Adicione todos os links que deseja antes de clicar em "Iniciar Download"
- ✓ Use MP4 para vídeos que pretende assistir
- ✓ Use MP3 para podcast, música ou conteúdo apenas de áudio
- ✓ Os downloads salvam automaticamente na pasta do Desktop
- ✓ Você pode minimizar a janela durante o download

---

## 📝 Licença

Este projeto está licenciado sob a Licença MIT - veja os detalhes para mais informações.

---

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir novas funcionalidades
- Melhorar a documentação

---

## 📧 Contato

Para dúvidas ou sugestões, abra uma issue no repositório.

---

<div align="center">

**Feito com ❤️ para facilitar o download do YouTube**

[⬆ Voltar ao topo](#-youtube-media-downloader)

</div>
4. Clique no botão "Download" para iniciar o processo.
5. Os arquivos baixados serão salvos na pasta "Downloads" do seu usuário, dentro das subpastas "Vídeos" ou "Músicas", conforme o formato escolhido.

## Estrutura do Projeto

```
├── main.py             # Script principal
└── README.md           # Documentação
```

## Contribuição

Contribuições são bem-vindas! Por favor, abra uma issue ou envie um pull request para discutir quaisquer alterações que você gostaria de fazer.

