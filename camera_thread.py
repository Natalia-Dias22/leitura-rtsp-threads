import cv2
import threading
import time


class CameraThread(threading.Thread):
    def __init__(self, nome, rtsp_url):
        super().__init__()
        self.nome = nome
        self.rtsp_url = rtsp_url

    def run(self):
        captura = cv2.VideoCapture(self.rtsp_url)

        if not captura.isOpened():
            print(f"Erro ao abrir a câmera {self.nome}")
            return

        print(f"Câmera {self.nome} iniciada com sucesso!")

        contador_frames = 0
        tempo_inicio = time.time()

        while True:
            ret, frame = captura.read()

            if not ret:
                print(f"Erro ao capturar o frame da câmera {self.nome}")
                break

            contador_frames += 1

            tempo_decorrido = time.time() - tempo_inicio
            fps = (
                contador_frames / tempo_decorrido
                if tempo_decorrido > 0
                else 0
            )

            texto = f"{self.nome} | FPS: {fps:.1f}"
            fonte = cv2.FONT_HERSHEY_SIMPLEX
            escala = 0.7
            espessura = 2

            (largura_texto, altura_texto), _ = cv2.getTextSize(
                texto,
                fonte,
                escala,
                espessura,
            )

            x, y = 10, 30

            cv2.rectangle(
                frame,
                (x - 5, y - altura_texto - 10),
                (x + largura_texto + 5, y + 5),
                (0, 0, 0),
                -1,
            )

            cv2.putText(
                frame,
                texto,
                (x, y),
                fonte,
                escala,
                (255, 255, 255),  # branco
                espessura,
                cv2.LINE_AA,
            )
            cv2.imshow(f"Câmera {self.nome}", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        captura.release()
        cv2.destroyAllWindows()