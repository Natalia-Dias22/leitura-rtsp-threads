# Documentação do Projeto: Leitura RTSP com Threads

## 1. Objetivo do projeto

Este projeto lê vídeos ou câmeras RTSP usando Python e OpenCV. A versão principal utiliza uma thread independente para cada câmera, permitindo que várias fontes sejam lidas ao mesmo tempo.

O projeto também possui:

- uma versão sequencial, sem threads, usada como referência;
- uma janela OpenCV que mostra um grid com os vídeos;
- um dashboard web feito com Streamlit;
- métricas de frames, FPS, tempo e vazão;
- um arquivo JSON com o resultado da execução sequencial.

A ideia principal é comparar duas formas de processamento:

1. **Sequencial:** uma câmera é processada por vez.
2. **Multithreading:** cada câmera é processada por uma thread própria.

---

## 2. Estrutura atual

```text
leitura-rtsp-threads/
|
|-- src/
|   |-- cameras/
|   |   |-- camera_thread.py
|   |
|   |-- display/
|   |   |-- grid_utils.py
|   |
|   |-- metrics/
|   |   |-- metrics_store.py
|   |
|   |-- web/
|   |   |-- dashboard.py
|   |
|   |-- config.py
|   |-- main.py
|   |-- __init__.py
|
|-- scripts/
|   |-- comparacao_sequencial.py
|   |-- __init__.py
|
|-- Video1.mp4
|-- Video2.mp4
|-- resultado_sequencial.json
|-- requirements.txt
|-- README.md
|-- DOCUMENTACAO_APRESENTACAO.md
```

As pastas `__pycache__` podem aparecer automaticamente depois que o Python executa ou compila os arquivos. Elas são arquivos temporários gerados pelo interpretador.

---

## 3. O que cada arquivo faz

### 3.1 `src/config.py`

Centraliza a configuração das câmeras.

Atualmente, a variável `CAMERAS` possui uma lista de tuplas. Cada tupla contém:

```python
("Nome da câmera", "caminho ou URL do vídeo")
```

Exemplo:

```python
CAMERAS = [
    ("Video-1", "C:\\leitura-rtsp-threads\\Video1.mp4"),
    ("Video-2", "C:\\leitura-rtsp-threads\\Video2.mp4"),
]
```

A vantagem de manter essa configuração separada é poder trocar os vídeos ou URLs sem alterar a lógica das threads.

Para usar uma câmera RTSP, basta substituir o caminho do arquivo por uma URL RTSP válida.

---

### 3.2 `src/cameras/camera_thread.py`

Contém a classe `CameraThread`, responsável por ler uma câmera em uma thread independente.

#### Classe `CameraThread`

A classe herda de `threading.Thread`:

```python
class CameraThread(threading.Thread):
```

Isso permite utilizar os métodos `.start()` e `.join()`.

#### Método `__init__(self, nome, rtsp_url)`

É o construtor da thread. Ele recebe:

- `nome`: nome usado para identificar a câmera;
- `rtsp_url`: caminho do vídeo ou URL RTSP.

Também cria os seguintes atributos:

- `contador_frames`: quantidade de frames lidos;
- `frame_atual`: último frame capturado;
- `rodando`: indica se o loop deve continuar;
- `fps`: taxa aproximada de frames por segundo daquela câmera.

#### Método `run(self)`

É o método executado quando chamamos:

```python
camera.start()
```

O método realiza estas etapas:

1. Abre o vídeo com `cv2.VideoCapture`.
2. Verifica se a fonte foi aberta corretamente.
3. Inicia o cronômetro da câmera.
4. Lê frames em um loop.
5. Incrementa `contador_frames` a cada frame válido.
6. Calcula o FPS da câmera.
7. Guarda o último frame em `frame_atual`.
8. Encerra ao atingir a duração do teste, ao receber uma falha de leitura ou quando `rodando` se torna falso.
9. Libera o recurso com `captura.release()`.

Quando um arquivo de vídeo chega ao fim, `capture.read()` retorna `False`. O código verifica a posição e a quantidade total de frames para mostrar `vídeo encerrado`, diferenciando esse encerramento normal de uma falha real de captura.

---

### 3.3 `src/display/grid_utils.py`

Possui a função responsável por montar uma imagem única com os frames de várias câmeras.

#### Função `montar_grid(frames, colunas=2, largura=500, altura=400)`

Parâmetros:

- `frames`: lista contendo os frames das câmeras;
- `colunas`: quantidade de câmeras por linha;
- `largura`: largura de cada imagem no grid;
- `altura`: altura de cada imagem no grid.

Funcionamento:

1. Se um frame ainda não existe, cria uma imagem preta com NumPy.
2. Redimensiona os frames existentes com `cv2.resize`.
3. Completa a última linha com imagens pretas, caso necessário.
4. Une os frames da mesma linha com `numpy.hstack`.
5. Une as linhas com `numpy.vstack`.
6. Retorna uma imagem única com todas as câmeras.

Essa função é usada pela janela OpenCV do `src/main.py`.

---

### 3.4 `src/main.py`

É o ponto de entrada da execução multithread com janela OpenCV.

Fluxo principal:

1. Importa a classe `CameraThread`, as câmeras configuradas e a função de grid.
2. Cria uma thread para cada item de `CAMERAS`.
3. Inicia todas as threads com `camera.start()`.
4. Enquanto alguma thread estiver ativa:
   - coleta `frame_atual` de cada câmera;
   - monta o grid;
   - exibe o resultado com `cv2.imshow`.
5. Se o usuário pressionar `q`, altera `rodando` para `False` em todas as câmeras.
6. Aguarda todas as threads terminarem com `camera.join()`.


O `start()` inicia a execução concorrente. O `join()` faz o programa principal esperar a finalização das threads antes de continuar.

Para executar estando dentro da pasta `src`:

```powershell
python main.py
```

Para executar a partir da raiz usando o ponto de entrada da raiz, quando ele estiver presente:

```powershell
python src/main.py
```

---

### 3.5 `src/metrics/metrics_store.py`

Contém a classe `MetricsStore`, que funciona como uma camada de métricas entre as threads e o dashboard.

Ela recebe a lista de câmeras e consulta os valores atuais de cada thread.

#### Método `__init__(self, cameras, tamanho_historico=100)`

Guarda as câmeras, inicia o cronômetro e cria um `deque` para armazenar até 100 amostras do histórico.

O `deque` evita que o histórico cresça indefinidamente durante uma execução longa.

#### Método `tempo_decorrido()`

Retorna quantos segundos se passaram desde a criação do `MetricsStore`.

#### Método `total_frames()`

Soma o contador de frames de todas as câmeras:

```text
total_frames = frames_camera_1 + frames_camera_2 + ...
```

#### Método `vazao_total()`

Calcula a vazão agregada do sistema:

```text
vazao_total = total_frames / tempo_decorrido
```

O resultado representa quantos frames, somando todas as câmeras, foram processados por segundo.

#### Método `metricas_por_camera()`

Monta uma lista com os dados atuais de cada câmera:

- nome;
- frames processados;
- FPS;
- status da thread.

O dashboard usa essa informação para mostrar o monitoramento individual.

#### Método `resumo()`

Retorna um dicionário com as métricas gerais:

- tempo decorrido;
- total de frames;
- vazão total;
- câmeras ativas;
- total de câmeras.

#### Método `registrar_amostra()`

Registra no histórico o tempo atual e a vazão atual. O dashboard chama esse método a cada atualização para alimentar o gráfico.

#### Método `historico()`

Retorna as amostras armazenadas para o gráfico de vazão.

#### Método `todas_finalizadas()`

Retorna `True` quando todas as threads já terminaram.

---

### 3.6 `src/web/dashboard.py`

É a aplicação web do projeto, executada com Streamlit.

Comando de execução:

```powershell
python -m streamlit run src/web/dashboard.py
```

O dashboard:

- cria e inicia as threads;
- guarda as threads em `st.session_state`;
- mostra os frames atuais dos vídeos;
- converte os frames de BGR para RGB antes de exibi-los;
- apresenta FPS e frames por câmera;
- mostra a vazão ao longo do tempo;
- compara multithreading com o resultado sequencial;
- mostra informações de telemetria.

#### Por que existe `st.session_state`?

O Streamlit reexecuta o arquivo quando a tela é atualizada. Sem `st.session_state`, cada atualização poderia criar novas threads e iniciar os vídeos novamente.

Guardando as câmeras em `st.session_state`, as mesmas threads continuam sendo utilizadas durante a sessão.

#### Exibição dos vídeos

A thread guarda o último frame neste atributo:

```python
camera.frame_atual
```

O dashboard converte o formato de cores usado pelo OpenCV:

```python
frame_rgb = cv2.cvtColor(camera.frame_atual, cv2.COLOR_BGR2RGB)
```

Depois exibe a imagem:

```python
st.image(frame_rgb, width="stretch")
```

O OpenCV trabalha normalmente em BGR, enquanto a exibição web espera RGB. A conversão evita que as cores apareçam invertidas.

#### Atualização em tempo real

Enquanto alguma câmera ainda está ativa, o dashboard espera um segundo e executa novamente:

```python
if not metrics_store.todas_finalizadas():
    time.sleep(1)
    st.rerun()
```

Assim, os frames e métricas são atualizados periodicamente.

---

### 3.7 `scripts/comparacao_sequencial.py`

É o programa usado para criar a referência sem threads.

Ele percorre as câmeras uma por vez:

1. Abre a primeira câmera.
2. Lê seus frames durante o teste.
3. Fecha a primeira câmera.
4. Abre a segunda câmera.
5. Repete o processo.
6. Soma os frames das câmeras.
7. Calcula o tempo total e a vazão.
8. Salva os resultados em `resultado_sequencial.json`.

A função principal é:

```python
executar_comparacao()
```

O bloco abaixo garante que a comparação só seja executada quando o arquivo for chamado diretamente:

```python
if __name__ == "__main__":
    executar_comparacao()
```

Para executar:

```powershell
python scripts/comparacao_sequencial.py
```

O arquivo é salvo na raiz do projeto, independentemente da pasta atual, usando o caminho obtido com `Path(__file__).resolve()`.

---

### 3.8 `resultado_sequencial.json`

É o arquivo de referência gerado pelo comparador sequencial.

Estrutura:

```json
{
  "vazao_total": 155.35,
  "total_frames": 2130,
  "tempo_total": 13.71
}
```

Significado dos campos:

- `vazao_total`: frames por segundo da execução sequencial;
- `total_frames`: quantidade total de frames processados;
- `tempo_total`: tempo total da execução em segundos.

O dashboard lê esse arquivo e compara a vazão sequencial com a vazão obtida pelas threads.

Esse arquivo deve ser gerado novamente sempre que os vídeos, câmeras ou condições do teste forem alterados.

---

### 3.9 `Video1.mp4` e `Video2.mp4`

São as fontes de vídeo usadas atualmente no teste.

Eles simulam duas câmeras. Em uma instalação real, podem ser substituídos por URLs RTSP.

Quando o arquivo termina, a leitura retorna `False` e a thread encerra normalmente.

---

### 3.10 `requirements.txt`

Lista as bibliotecas externas necessárias:

- `opencv-python`: leitura, conversão, redimensionamento e exibição de vídeos;
- `numpy`: criação e união das imagens do grid;
- `streamlit`: dashboard web;
- `pandas`: organização dos dados do histórico;
- `altair`: gráfico interativo de vazão.

Instalação:

```powershell
pip install -r requirements.txt
```

---

### 3.11 `README.md`

É o arquivo introdutório do projeto. Ele apresenta a ideia geral, os conceitos de threads e instruções básicas de execução.

Este documento complementa o README com uma explicação mais detalhada do funcionamento interno e um roteiro para apresentação.

---     '       

## 4. O que é vazão?

Vazão, também chamada de **throughput**, é a quantidade de trabalho processado em determinado intervalo de tempo.

Neste projeto, o trabalho é o processamento de frames. Por isso, a unidade usada é:

```text
frames por segundo
```

A fórmula é:

```text
Vazão = quantidade total de frames processados / tempo total em segundos
```

Exemplo:

```text
2.130 frames / 13,71 segundos = 155,36 frames por segundo
```

Isso significa que o programa processou, em média, 155,36 frames por segundo somando todas as câmeras durante aquele teste.

### Vazão não é exatamente a mesma coisa que FPS de uma câmera

- **FPS da câmera:** velocidade de uma câmera individual.
- **Vazão total:** quantidade de frames processados pelo sistema inteiro por segundo.

Por exemplo, duas câmeras podem apresentar aproximadamente 165 FPS cada. A vazão total do sistema pode ficar próxima de 330 frames por segundo, dependendo do tempo e da forma como a métrica é calculada.

A vazão é uma média. Ela pode mudar durante o teste por causa de:

- velocidade do computador;
- leitura do disco;
- resolução dos vídeos;
- compressão dos arquivos;
- rede, no caso de RTSP;
- processamento simultâneo das threads;
- tempo necessário para exibir as imagens.

---

## 5. Como funciona a comparação

### Execução sequencial

Na execução sequencial, o programa termina uma câmera antes de começar a próxima:

```text
Câmera 1 -> termina
Câmera 2 -> termina
```

Se a primeira câmera demorar ou travar, a segunda precisa esperar.

### Execução com threads

Na execução multithread, cada câmera possui sua própria thread:

```text
Thread da Câmera 1 -> lendo
Thread da Câmera 2 -> lendo ao mesmo tempo
```

Enquanto uma thread aguarda a leitura de uma fonte, as outras podem continuar trabalhando.

### Speedup

O ganho relativo pode ser calculado por:

```text
Speedup = vazão com threads / vazão sequencial
```

Exemplo:

```text
Speedup = 287,66 / 155,36 = 1,85x
```

Nesse caso, a execução com threads apresentou uma vazão aproximadamente 1,85 vezes maior que a execução sequencial.

O speedup depende do ambiente e não é necessariamente igual ao número de câmeras. Existem custos de leitura, exibição, sincronização e recursos compartilhados.

---

## 6. Conceitos de Sistemas Operacionais usados

### Thread

Uma thread é uma linha de execução dentro de um processo. Neste projeto, cada câmera possui uma thread própria.

### Concorrência

As threads progridem no mesmo período, compartilhando os recursos do processo.

### Paralelismo aparente

As câmeras são lidas de forma concorrente. A execução real depende do sistema operacional, do Python, do OpenCV e dos recursos do computador.

### Capacidade de resposta

Se uma câmera atrasar, as outras podem continuar sendo atualizadas. Isso evita que uma única fonte bloqueie completamente a aplicação.

### Compartilhamento de recursos

As threads compartilham o processo e as bibliotecas, mas cada câmera mantém seus próprios dados, como nome, contador e último frame.

### Sincronização de encerramento

O método `join()` garante que o programa principal aguarde as threads terminarem antes de calcular e exibir o resultado final.

---

## 7. Fluxo completo de execução

### Dashboard web

```text
Iniciar Streamlit
        |
        v
Ler configuração das câmeras
        |
        v
Criar uma CameraThread por câmera
        |
        v
Iniciar todas as threads
        |
        v
Cada thread lê e guarda seu último frame
        |
        v
Dashboard exibe frames e métricas
        |
        v
Atualizar a tela a cada segundo
        |
        v
Threads terminam quando o vídeo acaba
```

### Comparação sequencial

```text
Iniciar comparador
        |
        v
Abrir câmera 1 e ler seus frames
        |
        v
Fechar câmera 1
        |
        v
Abrir câmera 2 e ler seus frames
        |
        v
Calcular tempo, frames e vazão
        |
        v
Salvar resultado_sequencial.json
```

---

## 8. Ordem recomendada para demonstrar

1. Mostrar `src/config.py` e explicar que ele define as fontes.
2. Mostrar `CameraThread` e explicar que cada câmera roda em uma thread.
3. Executar a comparação sequencial:

   ```powershell
   python scripts/comparacao_sequencial.py
   ```

4. Mostrar que o JSON foi gerado.
5. Executar o dashboard:

   ```powershell
   python -m streamlit run src/web/dashboard.py
   ```

6. Mostrar os vídeos aparecendo nos cards.
7. Explicar as métricas de FPS, frames, tempo e vazão.
8. Comparar a barra de Multithreading com a barra Sequencial.
9. Explicar o speedup.
10. Mostrar que, quando os vídeos terminam, o sistema informa o encerramento normal.

---

## 9. Roteiro curto para falar na apresentação

> Este projeto demonstra a leitura simultânea de duas fontes de vídeo usando threads em Python. Cada câmera é representada por um objeto `CameraThread`, que herda de `threading.Thread`. O método `run` abre a fonte, lê os frames, atualiza o contador e guarda o último frame para ser exibido.
>
> Na versão sequencial, as câmeras são processadas uma por vez. Na versão multithread, cada câmera é iniciada em uma thread diferente. Isso permite que as fontes sejam lidas concorrentemente e melhora a capacidade de resposta da aplicação.
>
> A métrica principal é a vazão, que representa quantos frames o sistema processa por segundo. Ela é calculada dividindo o total de frames pelo tempo total da execução. O resultado sequencial é salvo em um arquivo JSON e usado pelo dashboard para comparar as duas abordagens.
>
> O dashboard web utiliza Streamlit. Ele mostra os vídeos atuais, o FPS de cada câmera, o total de frames, a vazão ao longo do tempo e o ganho obtido com o uso de threads.

---

## 10. Observação importante sobre os vídeos

Os arquivos atuais são vídeos locais. Por isso, quando chegam ao último frame, a leitura termina normalmente.

Em uma câmera RTSP real, a thread normalmente continuaria recebendo frames enquanto a conexão estivesse ativa. Nesse caso, uma falha de leitura pode indicar perda de conexão, indisponibilidade da câmera ou problema de rede.
