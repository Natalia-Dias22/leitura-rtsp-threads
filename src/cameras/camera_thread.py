import cv2
import threading
import time


class CameraThread(threading.Thread):
    def __init__(self, nome, rtsp_url):
        super().__init__()
        self.nome = nome
        self.rtsp_url = rtsp_url
        self.contador_frames = 0
        self.frame_atual = None
        self.rodando = True
        self.fps = 0.0

    def run(self):
        captura = cv2.VideoCapture(self.rtsp_url)

        if not captura.isOpened():
            print(f"Erro ao abrir a câmera {self.nome}")
            return

        print(f"Câmera {self.nome} iniciada com sucesso!")

        tempo_inicio = time.time()
        DURACAO_TESTE = 17
        fps_origem = captura.get(cv2.CAP_PROP_FPS)
        intervalo_frame = 1 / fps_origem if fps_origem > 0 else 0

        while self.rodando:
            if time.time() - tempo_inicio > DURACAO_TESTE:
                print(f"{self.nome}: tempo de teste encerrado")
                break

            ret, frame = captura.read()

            if not ret:
                total_frames_video = captura.get(cv2.CAP_PROP_FRAME_COUNT)
                frame_atual = captura.get(cv2.CAP_PROP_POS_FRAMES)
                if total_frames_video > 0 and frame_atual >= total_frames_video:
                    print(f"{self.nome}: vídeo encerrado")
                else:
                    print(f"Erro ao capturar o frame da câmera {self.nome}")
                break

            self.contador_frames += 1
            tempo_decorrido = time.time() - tempo_inicio
            self.fps = self.contador_frames / tempo_decorrido if tempo_decorrido > 0 else 0

            self.frame_atual = frame

            if intervalo_frame > 0:
                time.sleep(intervalo_frame)

        captura.release()