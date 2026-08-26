# Leitura de Canais RTSP em Paralelo com Python (Threads)

Trabalho prático da disciplina de **Sistemas Operacionais** — Capítulo 04: Threads.

##  Sobre o projeto

Esta aplicação demonstra o uso de **Threads** para resolver um problema real: a leitura simultânea de múltiplas fontes de vídeo (câmeras RTSP ou arquivos de vídeo), sem que a leitura de uma fonte trave ou atrase a leitura das outras.

Cada câmera é tratada como uma **Thread independente**, que fica em loop lendo os frames daquela fonte específica, exibindo o vídeo em tempo real com um contador de FPS sobreposto.

##  Problema resolvido

Ler vídeo de uma fonte (especialmente uma câmera de rede via RTSP) não é uma operação instantânea — há atraso de rede, variações de banda, e possíveis travamentos momentâneos. Se a leitura de várias câmeras fosse feita de forma **sequencial** (uma de cada vez, no mesmo fluxo de execução), um atraso em uma única câmera bloquearia a leitura de todas as outras.

Usando **múltiplas Threads**, cada câmera roda de forma **concorrente e independente**: se uma câmera travar ou demorar para responder, as demais continuam sendo lidas e exibidas normalmente.

Esse comportamento está diretamente ligado ao conceito de **Capacidade de Resposta**, um dos benefícios do uso de Threads:

> "O uso de várias Threads em uma aplicação pode permitir que um programa continue a ser executado mesmo se parte dele estiver bloqueada ou executando uma operação demorada."

## Conceitos de Sistemas Operacionais aplicados

| Conceito da teoria | Onde aparece no projeto |
|---|---|
| **Thread** | Cada câmera é representada por um objeto `CameraThread`, uma unidade independente de execução |
| **Multithreading** | O processo principal (`main.py`) cria e executa várias Threads simultaneamente |
| **Capacidade de Resposta** | Uma câmera travando não impede a exibição das demais |
| **Compartilhamento de recursos** | Todas as Threads compartilham o mesmo processo e a biblioteca `cv2`, mas cada uma mantém seus próprios dados (`nome`, `rtsp_url`) de forma isolada via `self` |
| **Concorrência / Não-determinismo** | A ordem de execução entre as Threads não é fixa — depende do escalonamento feito pelo sistema operacional |
| **Herança (Thread como classe base)** | `CameraThread` estende `threading.Thread`, reaproveitando os métodos `.start()` e `.join()` |

## 📂 Estrutura do projeto

```
leitura-rtsp-threads/
│
├── main.py                    # ponto de entrada: cria, inicia e finaliza as threads
├── camera_thread.py           # classe CameraThread (herda de threading.Thread)
├── config.py                  # lista de câmeras (nome + URL/caminho de cada uma)
├── comparacao_sequencial.py   # versão SEM threads, para fins de comparação
├── requirements.txt           # dependências do projeto
└── README.md                  # este arquivo
```

##  Como executar

### 1. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar as fontes de vídeo

Edite o arquivo `config.py` com os caminhos dos seus vídeos ou URLs RTSP:

```python
CAMERAS = [
    ("Video-1", "caminho/ou/url/da/camera1"),
    ("Video-2", "caminho/ou/url/da/camera2"),
]
```

### 3. Rodar a versão com Threads (principal)

```bash
python main.py
```

### 4. (Opcional) Rodar a versão sequencial, para comparação

```bash
python comparacao_sequencial.py
```

> Durante a execução, pressione **"q"** em qualquer janela para encerrar a leitura daquela fonte de vídeo.

##  Tecnologias utilizadas

- **Python 3**
- **OpenCV** (`opencv-python`) — captura e exibição de vídeo
- **threading** — biblioteca nativa do Python para criação e gerenciamento de Threads
