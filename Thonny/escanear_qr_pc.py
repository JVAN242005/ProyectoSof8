import cv2
from pyzbar.pyzbar import decode
import requests

API_URL = "http://10.92.255.218:8000/api/asistencias/qr"  # Cambia por la IP de tu PC
API_RESULTADO = "http://10.92.255.218:8000/api/resultado"

def escanear_qr():
    cap = cv2.VideoCapture(0)
    print("Apunta el QR a la cámara... (presiona 'q' para salir)")
    qr_detectado = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        for barcode in decode(frame):
            qr_data = barcode.data.decode('utf-8')
            print("QR detectado:", qr_data)
            qr_detectado = qr_data
            # Dibuja un rectángulo alrededor del QR
            pts = barcode.polygon
            pts = [(pt.x, pt.y) for pt in pts]
            pts = pts + [pts[0]]
            for i in range(len(pts)-1):
                cv2.line(frame, pts[i], pts[i+1], (0,255,0), 2)
            cv2.putText(frame, qr_data, (barcode.rect.left, barcode.rect.top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        cv2.imshow('Lector QR', frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or qr_detectado:
            break

    cap.release()
    cv2.destroyAllWindows()
    return qr_detectado

def enviar_qr_al_backend(qr_text):
    if qr_text:
        res = requests.post(API_URL, json={"qr_texto": qr_text})
        print("Respuesta del backend:")
        print("Código de estado:", res.status_code)
        print("Texto de respuesta:", res.text)
    else:
        print("No se detectó ningún QR.")

def notificar_esp32_exito():
    # Cambia el estado para que la ESP32 encienda la LED verde
    requests.post(API_RESULTADO, json={"estado": "ok", "mensaje": "QR registrado"})

if __name__ == "__main__":
    qr_text = escanear_qr()
    enviar_qr_al_backend(qr_text)
    if qr_text:
        print("QR registrado")
        notificar_esp32_exito()