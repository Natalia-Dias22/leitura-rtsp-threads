import cv2
from config import CAMERAS

for nome, url in CAMERAS:
    print(f"Iniciando {nome}...")
    captura = cv2.VideoCapture(url)

    if not captura.isOpened():
        print(f"Erro ao abrir {nome}")
        continue

    while True:
        ret, frame = captura.read()
        if not ret:
            break

        cv2.imshow(nome, frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    captura.release()
    cv2.destroyWindow(nome)  

print("Todas finalizadas!")