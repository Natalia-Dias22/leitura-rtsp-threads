import cv2
import numpy as np


def montar_grid(frames, colunas=2, largura=500, altura=400):
    """Monta uma imagem com os frames das câmeras organizados em um grid."""
    frames_redimensionados = []

    for frame in frames:
        if frame is None:
            frame = np.zeros((altura, largura, 3), dtype=np.uint8)
        else:
            frame = cv2.resize(frame, (largura, altura))

        frames_redimensionados.append(frame)

    if not frames_redimensionados:
        return np.zeros((altura, largura, 3), dtype=np.uint8)

    linhas = []
    for i in range(0, len(frames_redimensionados), colunas):
        linha_frames = frames_redimensionados[i:i + colunas]

        while len(linha_frames) < colunas:
            linha_frames.append(np.zeros((altura, largura, 3), dtype=np.uint8))

        linhas.append(np.hstack(linha_frames))

    return np.vstack(linhas)
