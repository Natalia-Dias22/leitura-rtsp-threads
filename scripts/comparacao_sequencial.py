import json
import sys
import time
from pathlib import Path

import cv2


RAIZ_PROJETO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_PROJETO))

from src.config import CAMERAS  # noqa: E402


DURACAO_TESTE = 17


def executar_comparacao():
    tempo_inicio_geral = time.time()
    total_frames = 0

    for nome, url in CAMERAS:
        print(f"Iniciando {nome}...")
        captura = cv2.VideoCapture(url)
        contador_frames = 0

        if not captura.isOpened():
            print(f"Erro ao abrir {nome}")
            captura.release()
            continue

        fps_origem = captura.get(cv2.CAP_PROP_FPS)
        intervalo_frame = 1 / fps_origem if fps_origem > 0 else 0
        tempo_inicio_camera = time.time()
        try:
            while time.time() - tempo_inicio_camera <= DURACAO_TESTE:
                ret, frame = captura.read()
                if not ret:
                    total_frames_video = captura.get(cv2.CAP_PROP_FRAME_COUNT)
                    frame_atual = captura.get(cv2.CAP_PROP_POS_FRAMES)
                    if total_frames_video > 0 and frame_atual >= total_frames_video:
                        print(f"{nome}: vídeo encerrado")
                    else:
                        print(f"Erro ao capturar um frame de {nome}")
                    break

                contador_frames += 1
                cv2.imshow(nome, frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

                if intervalo_frame > 0:
                    time.sleep(intervalo_frame)
        finally:
            captura.release()
            cv2.destroyWindow(nome)

        total_frames += contador_frames
        print(f"  {nome} finalizada: {contador_frames} frames")

    tempo_total = time.time() - tempo_inicio_geral
    vazao_total = total_frames / tempo_total if tempo_total > 0 else 0
    resultado = {
        "vazao_total": vazao_total,
        "total_frames": total_frames,
        "tempo_total": tempo_total,
    }

    caminho_resultado = RAIZ_PROJETO / "resultado_sequencial.json"
    caminho_resultado.write_text(
        json.dumps(resultado, indent=2),
        encoding="utf-8",
    )

    print("\n--- Métricas de Desempenho (SEM Threads / Sequencial) ---")
    print(f"Tempo total de execução: {tempo_total:.2f}s")
    print(f"Total de frames processados: {total_frames}")
    print(f"Vazão (throughput): {vazao_total:.2f} frames/segundo")
    print(f"Resultado salvo em: {caminho_resultado}")


if __name__ == "__main__":
    executar_comparacao()