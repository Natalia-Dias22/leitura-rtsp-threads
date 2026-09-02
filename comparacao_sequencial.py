import cv2
import time
from config import CAMERAS

DURACAO_TESTE = 5

tempo_inicio_geral = time.time()
total_frames = 0

for nome, url in CAMERAS:
    print(f"Iniciando {nome}...")
    captura = cv2.VideoCapture(url)

    if not captura.isOpened():
        print(f"Erro ao abrir {nome}")
        continue

    contador_frames = 0
    tempo_inicio_camera = time.time()

    while True:
        if time.time() - tempo_inicio_camera > DURACAO_TESTE:
            print(f"{nome}: tempo de teste encerrado")
            break
     
        ret, frame = captura.read()
        if not ret:
            break

        contador_frames += 1

        cv2.imshow(nome, frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    captura.release()
    cv2.destroyWindow(nome)  # fecha só a janela dessa câmera, antes de ir para a próxima

    total_frames += contador_frames
    print(f"  {nome} finalizada: {contador_frames} frames")

tempo_total = time.time() - tempo_inicio_geral
vazao = total_frames / tempo_total if tempo_total > 0 else 0

print("\n--- Métricas de Desempenho (SEM Threads / Sequencial) ---")
print(f"Tempo total de execução: {tempo_total:.2f}s")
print(f"Total de frames processados (todas as câmeras): {total_frames}")
print(f"Vazão (throughput): {vazao:.2f} frames/segundo")
