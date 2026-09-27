"""
Script de comparação SEM threads (sequencial).

Objetivo: rodar UMA VEZ, capturando cada câmera por um tempo fixo
(DURACAO_TESTE), uma de cada vez, e salvar o resultado (tempo total,
frames processados, vazão) em um arquivo JSON na raiz do projeto.

Esse JSON serve como "número de referência" para o dashboard web
comparar com a versão com Threads, sem precisar rodar a versão
sequencial novamente durante a apresentação.
"""

import os
import sys
import json
import time

import cv2

# Permite importar o config.py de dentro de src/, mesmo este script
# estando em uma pasta separada (scripts/)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from config import CAMERAS  # noqa: E402


DURACAO_TESTE = 30 


def rodar_comparacao_sequencial():
    tempo_inicio_geral = time.time()
    total_frames = 0
    por_camera = []  # guarda o resultado individual de cada câmera

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
        cv2.destroyWindow(nome)

        tempo_camera = time.time() - tempo_inicio_camera
        total_frames += contador_frames
        # Guardamos frames e tempo desta câmera isoladamente. Como no modo
        # sequencial cada câmera roda sozinha (seu tempo não depende de
        # quantas outras existem na lista), depois dá pra somar só as N
        # primeiras entradas daqui pra simular "sequencial com N câmeras",
        # sem precisar rodar este script de novo.
        por_camera.append({
            "nome": nome,
            "frames": contador_frames,
            "tempo": round(tempo_camera, 2),
        })
        print(f"  {nome} finalizada: {contador_frames} frames")

    tempo_total = time.time() - tempo_inicio_geral
    vazao = total_frames / tempo_total if tempo_total > 0 else 0

    resultado = {
        "tempo_total": round(tempo_total, 2),
        "total_frames": total_frames,
        "vazao_total": round(vazao, 2),
        "duracao_teste_por_camera": DURACAO_TESTE,
        "quantidade_cameras": len(CAMERAS),
        "por_camera": por_camera,
    }

    caminho_saida = os.path.join(os.path.dirname(__file__), '..', 'resultado_sequencial.json')
    with open(caminho_saida, 'w', encoding='utf-8') as arquivo:
        json.dump(resultado, arquivo, indent=2, ensure_ascii=False)

    print("\n--- Métricas de Desempenho (SEM Threads / Sequencial) ---")
    print(f"Tempo total de execução: {tempo_total:.2f}s")
    print(f"Total de frames processados: {total_frames}")
    print(f"Vazão (throughput): {vazao:.2f} frames/segundo")
    print(f"\nResultado salvo em: {os.path.abspath(caminho_saida)}")


if __name__ == "__main__":
    rodar_comparacao_sequencial()