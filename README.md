# Leitura de Canais RTSP em Paralelo com Python (Threads)

Trabalho prático da disciplina de **Sistemas Operacionais** 

##  Sobre o projeto

Esta aplicação demonstra o uso de **Threads** para resolver um problema real: a leitura simultânea de múltiplas fontes de vídeo (câmeras RTSP ou arquivos de vídeo), sem que a leitura de uma fonte trave ou atrase a leitura das outras.

Cada câmera é tratada como uma **Thread independente**, que fica em loop lendo os frames daquela fonte específica. O projeto inclui um **dashboard web interativo** (Streamlit), com vídeo ao vivo, métricas de desempenho em tempo real e um controle de escalabilidade que permite ativar de 1 até N câmeras/threads simultaneamente.

## Problema resolvido

Ler vídeo de uma fonte (especialmente uma câmera de rede via RTSP) não é uma operação instantânea — há atraso de rede, variações de banda, e possíveis travamentos momentâneos. Se a leitura de várias câmeras fosse feita de forma **sequencial** (uma de cada vez, no mesmo fluxo de execução), um atraso em uma única câmera bloquearia a leitura de todas as outras.

Usando **múltiplas Threads**, cada câmera roda de forma **concorrente e independente**: enquanto uma está esperando dados chegarem (I/O), as demais continuam sendo processadas — sem que nenhuma trave a outra.

É importante destacar que o projeto demonstra **concorrência**, não paralelismo puro de CPU: as Threads são iniciadas uma após a outra (`.start()`), mas nenhuma espera a anterior terminar para começar.

##  Conceitos de Sistemas Operacionais aplicados

| Conceito da teoria | Onde aparece no projeto |
|---|---|
| **Thread** | Cada câmera é representada por um objeto `CameraThread`, uma unidade independente de execução |
| **Multithreading** | O dashboard cria e executa várias Threads simultaneamente, uma por câmera |
| **Concorrência vs. Paralelismo** | As câmeras são lidas de forma concorrente (I/O-bound); não há garantia de execução simultânea real de CPU |
| **Ciclo de vida de uma Thread** | `start()` inicia a execução em `run()`; `join()` garante que o programa principal espere todas as Threads terminarem antes de seguir |
| **Compartilhamento de memória** | Threads de um mesmo processo compartilham o mesmo espaço de memória, o que as torna mais leves de criar do que Processos |
| **Estado compartilhado** | Cada `CameraThread` mantém seus próprios atributos (`contador_frames`, `fps`, `frame_atual`) como `self`, lidos pela thread principal sem uso explícito de `Lock` |
| **Não-determinismo** | A ordem de execução e o tempo de CPU dado a cada Thread são decididos pelo sistema operacional a cada execução — por isso os resultados de vazão variam entre rodadas, mesmo sem mudar o código |
| **Herança (Thread como classe base)** | `CameraThread` estende `threading.Thread`, reaproveitando os métodos `.start()` e `.join()` |

## 📂 Estrutura do projeto

```
leitura-rtsp-threads/
│
├── src/
│   ├── main.py                     # ponto de entrada: grid de vídeo via OpenCV (sem interface web)
│   ├── config.py                   # lista de câmeras (nome + URL/caminho de cada uma)
│   │
│   ├── cameras/
│   │   └── camera_thread.py        # classe CameraThread (herda de threading.Thread)
│   │
│   ├── display/
│   │   └── grid_utils.py           # monta um grid único a partir dos frames de várias câmeras
│   │
│   ├── metrics/
│   │   └── metrics_store.py        # calcula vazão, tempo decorrido e histórico de amostras
│   │
│   └── web/
│       └── dashboard.py            # dashboard Streamlit (interface principal do projeto)
│
├── scripts/
│   └── comparacao_sequencial.py    # versão SEM threads, gera o JSON de referência
│
├── resultado_sequencial.json       # gerado pelo script acima — NÃO editar manualmente
├── requirements.txt                # dependências do projeto
└── README.md                       # este arquivo
```

##  Como funciona

### `cameras/camera_thread.py`

Define a classe `CameraThread`, que herda de `threading.Thread`. Cada objeto representa **uma câmera/fonte de vídeo independente**, responsável por:

- Abrir a conexão com a fonte de vídeo (`cv2.VideoCapture`);
- Ler os frames continuamente, em loop, por um tempo máximo (`DURACAO_TESTE`);
- Calcular a vazão de processamento (`fps = frames ÷ tempo decorrido`) e guardar o frame mais recente em `self.frame_atual`, para o dashboard exibir;
- Encerrar e liberar seus próprios recursos ao final.

> A thread **não** chama `cv2.imshow`/`cv2.waitKey` — isso é proposital, para evitar conflito entre janelas de diferentes threads e não adicionar overhead artificial ao loop de captura.

### `config.py`

Contém apenas a lista de câmeras, separada da lógica de execução — facilita trocar as fontes de vídeo sem precisar mexer no restante do código.

### `metrics/metrics_store.py`

Centraliza o cálculo das métricas: vazão total, frames processados, tempo decorrido, resumo por câmera e histórico de amostras (usado para montar gráficos).

### `web/dashboard.py`

Interface principal do projeto, em Streamlit, dividida em duas abas:

- **📷 Câmeras** — vídeo ao vivo de cada fonte, com FPS individual e status (ativa/finalizada);
- **📊 Métricas** — gráfico de **vazão por número de threads ativas** (comparando Threads medido x Sequencial projetado), comparação Threads vs. Sequencial para o N atual, e telemetria geral do sistema.

Inclui também um **controle de escalabilidade** (slider), que permite escolher quantas câmeras/threads ficam ativas (de 1 até o total configurado). Ao mudar o valor, as threads são reiniciadas automaticamente com aquele número de câmeras — permitindo observar, na prática, como a vazão se comporta conforme o número de threads aumenta (nem sempre de forma linear, já que depende da CPU disponível e da complexidade de cada vídeo).

### `scripts/comparacao_sequencial.py`

Versão alternativa **sem uso de Threads**: cada câmera é lida por completo, uma de cada vez, antes de passar para a próxima. Salva o resultado em `resultado_sequencial.json`, incluindo:

- O total agregado (frames, tempo, vazão);
- Os dados **individuais de cada câmera** (`por_camera`), permitindo calcular a vazão sequencial equivalente para **qualquer número de câmeras**, sem precisar rodar o script novamente — basta somar os dados das N primeiras câmeras da lista, já que cada uma roda de forma isolada, sem depender das demais.

> Esse script deve ser executado **antes** da apresentação (uma única vez), pois roda de forma sequencial e pode levar bastante tempo.

### `main.py` + `display/grid_utils.py` (opcional)

Versão alternativa ao dashboard: mostra as câmeras num grid único de janela OpenCV, sem interface web. Útil como demonstração rápida via terminal, mas menos completa que o dashboard.

##  Como executar

### 1. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar as fontes de vídeo

Edite `src/config.py` com os caminhos dos seus vídeos ou URLs RTSP:

```python
CAMERAS = [
    ("Video-1", "caminho/ou/url/da/camera1"),
    ("Video-2", "caminho/ou/url/da/camera2"),
]
```

### 3. Gerar o JSON de referência sequencial (rodar uma vez)

```bash
cd scripts
python comparacao_sequencial.py
cd ..
```

> Repita esse passo sempre que adicionar ou trocar câmeras em `config.py`, para manter a referência sequencial atualizada.

### 4. Rodar o dashboard (interface principal)

```bash
python -m streamlit run src/web/dashboard.py
```

### 5. (Opcional) Rodar a versão em grid, via OpenCV

```bash
cd src
python main.py
```

##  Resultado esperado

- **Aba Câmeras**: vídeo ao vivo de cada fonte, atualizado a cada segundo (limitação da arquitetura do Streamlit, que re-executa a página inteira a cada refresh — as threads continuam capturando na velocidade real por trás disso).
- **Aba Métricas**: gráfico de vazão por número de threads ativas, comparação Threads vs. Sequencial, e telemetria geral.
- **Controle de threads**: ao mover o slider, é possível observar que aumentar o número de câmeras **não garante** aumento proporcional de vazão — depende da capacidade do processador em decodificar múltiplos vídeos ao mesmo tempo.

##  Tecnologias utilizadas

- **Python 3**
- **OpenCV** (`opencv-python`) — captura de vídeo
- **threading** — biblioteca nativa do Python para criação e gerenciamento de Threads
- **Streamlit** — dashboard web interativo
- **Altair** + **Pandas** — gráficos e manipulação de dados de métricas

\s