# ESP32 MicroPython (SIN OLED, consulta backend y controla LEDs/buzzer, compatible con buzzer pasivo)
import network
import urequests
import time
from machine import Pin, PWM

# Configuración de pines para LEDs y buzzer
led_verde = Pin(19, Pin.OUT)      # LED verde en GPIO 19
led_amarillo = Pin(15, Pin.OUT)   # LED amarillo en GPIO 15
led_rojo = Pin(18, Pin.OUT)       # LED rojo en GPIO 18
buzzer_pin = 4                    # Buzzer en GPIO 4

# Función para conectar la ESP32 a una red WiFi
def conectar_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    intentos = 0
    while not wlan.isconnected():
        time.sleep(1)
        intentos += 1
        print(f"Intentando conectar WiFi... ({intentos})")
        if intentos > 15:
            print("No se pudo conectar a WiFi.")
            return False
    print('WiFi conectado:', wlan.ifconfig())
    return True

# Función para sonar el buzzer (compatible con buzzer pasivo)
def sonar_buzzer(duracion=0.1, frecuencia=1000):
    try:
        pwm = PWM(Pin(buzzer_pin))
        pwm.freq(frecuencia)
        pwm.duty(100)  # Intensidad media (0-1023)
        time.sleep(duracion)
        pwm.deinit()
    except Exception as e:
        print("Error al activar el buzzer:", e)

# Función para mostrar el resultado en LEDs y buzzer (SIN OLED)
def mostrar_resultado(estado, mensaje):
    # Apaga todos los LEDs
    led_verde.off()
    led_amarillo.off()
    led_rojo.off()
    print("DEBUG Estado recibido:", estado)
    print("DEBUG Mensaje recibido:", mensaje)
    # Enciende el LED y activa el buzzer según el estado recibido
    if estado == "ok":
        print("Acción: LED VERDE y buzzer 2s")
        led_verde.on()
        sonar_buzzer(2)
        led_verde.off()
    elif estado == "advertencia":
        print("Acción: LED AMARILLO y buzzer 0.2s")
        led_amarillo.on()
        sonar_buzzer(0.2)
        led_amarillo.off()
    else:
        print("Acción: LED ROJO y buzzer 0.2s")
        led_rojo.on()
        sonar_buzzer(0.1)
        led_rojo.off()

# Función para consultar el backend y obtener el resultado del QR (con mejor control de errores)
def consultar_backend():
    try:
        url = "http://10.92.255.218:8000/api/esp32/resultado"  # Cambia TU_IP_LOCAL por la IP de tu PC
        print(f"Consultando backend: {url}")
        res = urequests.get(url)
        print("HTTP status:", res.status_code)
        print("Raw response:", res.text)
        if res.status_code == 200:
            try:
                data = res.json()
                print("DEBUG JSON recibido:", data)
                estado = data.get("estado")
                mensaje = data.get("mensaje")
                if estado is None or mensaje is None:
                    print("ERROR: El JSON no tiene los campos 'estado' o 'mensaje'")
                mostrar_resultado(estado, mensaje)
            except Exception as e:
                print("ERROR al parsear JSON:", e)
                mostrar_resultado("error", "JSON inválido")
        else:
            print("ERROR: Código HTTP inesperado:", res.status_code)
            mostrar_resultado("error", f"HTTP {res.status_code}")
    except Exception as e:
        import sys
        print("Exception type:", type(e))
        print("Exception details:", e)
        mostrar_resultado("error", "Error red")

# --- USO ---
if conectar_wifi("Kameron", "12345678"):
    while True:
        consultar_backend()
        time.sleep(2)  # Consulta cada 2 segundos
else:
    print("No se pudo conectar a la red WiFi. Revisa SSID y contraseña.")

'''
¿La red WiFi necesita internet?
NO es necesario que la red tenga acceso a internet.
Solo es necesario que la ESP32 y tu PC estén conectados a la misma red local (WiFi o router).
El backend FastAPI debe ser accesible desde la ESP32 usando la IP local de tu PC.
'''
