import cv2
import time
from camera_thread import CameraThread
from config import CAMERAS
from grid_utils import montar_grid


cameras = [CameraThread(nome, url) for nome, url in CAMERAS]

tempo_inicio_geral = time.time()

for camera in cameras:
    camera.start()

while any(camera.is_alive() for camera in cameras):
    frames = [camera.frame_atual for camera in cameras]
    grid = montar_grid(frames, colunas=2)
 
    cv2.imshow("Cameras - Grid", grid)
 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        for camera in cameras:
            camera.rodando = False  # sinaliza para todas as threads pararem
        break

for camera in cameras:
    camera.join()

tempo_total = time.time() - tempo_inicio_geral


cv2.destroyAllWindows()

# --- Métricas (parte nova) ---
total_frames = sum(camera.contador_frames for camera in cameras)
vazao = total_frames / tempo_total if tempo_total > 0 else 0

print("\n--- Métricas de Desempenho (COM Threads) ---")
print(f"Tempo total de execução: {tempo_total:.2f}s")
print(f"Total de frames processados: {total_frames}")
print(f"Vazão (throughput): {vazao:.2f} frames/segundo")

for camera in cameras:
    print(f"  - {camera.nome}: {camera.contador_frames} frames")