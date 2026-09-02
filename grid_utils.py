import cv2
import numpy as np


def montar_grid(frames, colunas=2, largura=500, altura=400):
    """
    Recebe uma lista de frames (imagens) de diferentes câmeras e monta
    uma única imagem, organizando-os lado a lado em um grid.

    - frames: lista de imagens (cada uma pode ser None, caso a câmera
      ainda não tenha capturado nenhum frame)
    - colunas: quantas câmeras ficam por linha
    - largura, altura: tamanho que cada câmera vai ocupar dentro do grid
    """
    frames_redimensionados = []

    for frame in frames:
        if frame is None:
            # Se a câmera ainda não tem frame, mostra um quadro preto no lugar
            frame = np.zeros((altura, largura, 3), dtype=np.uint8)
        else:
            frame = cv2.resize(frame, (largura, altura))

        frames_redimensionados.append(frame)

    linhas = []
    for i in range(0, len(frames_redimensionados), colunas):
        linha_frames = frames_redimensionados[i:i + colunas]

        # Se a última linha não tiver câmeras suficientes para preencher
        # todas as colunas, completa com quadros pretos
        while len(linha_frames) < colunas:
            linha_frames.append(np.zeros((altura, largura, 3), dtype=np.uint8))

        linha = np.hstack(linha_frames)  # junta as imagens da linha, lado a lado
        linhas.append(linha)

    grid = np.vstack(linhas)  # junta as linhas, uma embaixo da outra
    return grid