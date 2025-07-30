#@title create project
from newreg import *
import requests
import os
import requests
from urllib.parse import quote_plus
import subprocess
import time
import datetime
import requests
import re

# Variable global para permitir detener el bucle desde otra función
stop_flag = False



def mostrar_barra(progreso, longitud=40):
    llenos = int(longitud * progreso)
    barra = '=' * llenos + '-' * (longitud - llenos)
    porcentaje = round(progreso * 100, 2)
    print(f"\r[{barra}] {porcentaje:.2f}%", end="", flush=True)

def obtener_duracion(video):
    comando = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=nw=1",
        video
    ]
    resultado = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    salida = resultado.stdout.strip()

    if '=' in salida:
        salida = salida.split('=')[1]

    return float(salida)

def obtener_resolucion(video):
    comando = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height",
        "-of", "csv=p=0",
        video
    ]
    resultado = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return map(int, resultado.stdout.strip().split(','))

# =============================================
# ✅ Función: Agregar franja negra arriba
# =============================================
def agregar_franja_negra(video_entrada, video_salida, altura_franja=70):
    if not os.path.exists(video_entrada):
        print(f"⚠️ Archivo de entrada '{video_entrada}' no encontrado.")
        return

    try:
        duracion_total = obtener_duracion(video_entrada)
    except Exception as e:
        print(f"❌ No se pudo obtener la duración del video: {e}")
        return

    try:
        ancho, alto = obtener_resolucion(video_entrada)
    except Exception as e:
        print(f"❌ No se pudo obtener la resolución del video: {e}")
        return

    nuevo_alto = alto + altura_franja

    print(f"🎬 Resolución original: {ancho}x{alto}")
    #print(f"🔺 Añadiendo franja de {altura_franja}px arriba → Nueva resolución: {ancho}x{nuevo_alto}")

    comando = [
        "ffmpeg",
        "-y",
        "-i", video_entrada,
        "-vf", f"pad={ancho}:{nuevo_alto}:0:{altura_franja}:black",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "fastdecode",
        "-crf", "28",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        "-progress", "pipe:1",
        "-nostats",
        video_salida
    ]

    log_salida = []

    proceso = subprocess.Popen(comando, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, universal_newlines=True)

    tiempo_actual = 0
    for linea in proceso.stdout:
        linea = linea.strip()
        log_salida.append(linea)
        if linea.startswith("out_time_ms"):
            try:
                valor = linea.split("=")[1]
                tiempo_actual = int(valor) / 1_000_000
            except (ValueError, IndexError):
                continue
        elif linea.startswith("progress") and "end" in linea:
            break

        progreso = min(tiempo_actual / duracion_total, 1.0)
        mostrar_barra(progreso)

    proceso.stdout.close()
    proceso.wait()

    if proceso.returncode == 0:
        print("\n✅ Franja añadida correctamente.")
    else:
        print("\n❌ Error al procesar el video. Detalles:")
        for linea in log_salida:
            print(f"  {linea}")

# =============================================
# ✅ Función: Recortar franja negra arriba
# =============================================
def recortar_franja_negra(video_entrada, video_salida, altura_franja=70):
    if not os.path.exists(video_entrada):
        print(f"⚠️ Archivo de entrada '{video_entrada}' no encontrado.")
        return

    try:
        duracion_total = obtener_duracion(video_entrada)
    except Exception as e:
        print(f"❌ No se pudo obtener la duración del video: {e}")
        return

    try:
        ancho, alto = obtener_resolucion(video_entrada)
    except Exception as e:
        print(f"❌ No se pudo obtener la resolución del video: {e}")
        return

    nuevo_alto = alto - altura_franja

    if nuevo_alto <= 0:
        print("❌ El alto resultante es inválido (menor o igual a cero).")
        return

    print(f"✂️ Resolución original: {ancho}x{alto}")
    #print(f"🔻 Recortando {altura_franja}px arriba → Nueva resolución: {ancho}x{nuevo_alto}")

    comando = [
        "ffmpeg",
        "-y",
        "-i", video_entrada,
        "-vf", f"crop={ancho}:{nuevo_alto}:0:{altura_franja}",
        "-c:a", "copy",
        "-progress", "pipe:1",
        "-nostats",
        video_salida
    ]

    log_salida = []

    proceso = subprocess.Popen(comando, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, universal_newlines=True)

    tiempo_actual = 0
    for linea in proceso.stdout:
        linea = linea.strip()
        log_salida.append(linea)
        if linea.startswith("out_time_ms"):
            try:
                valor = linea.split("=")[1]
                tiempo_actual = int(valor) / 1_000_000
            except (ValueError, IndexError):
                continue
        elif linea.startswith("progress") and "end" in linea:
            break

        progreso = min(tiempo_actual / duracion_total, 1.0)
        mostrar_barra(progreso)

    proceso.stdout.close()
    proceso.wait()

    if proceso.returncode == 0:
        print("\n✅ Franja recortada correctamente.")
    else:
        print("\n❌ Error al procesar el video. Detalles:")
        for linea in log_salida:
            print(f"  {linea}")





def delete_project(session_token: str, project_id: str):
    """
    Elimina un proyecto de sync.so usando el endpoint /trpc/projects.delete

    Args:
        session_token (str): Token de sesión (__Secure-sync.session_token)
        project_id (str): ID del proyecto a eliminar

    Returns:
        dict: Respuesta de la API o mensaje de error
    """
    url = "https://api.sync.so/trpc/projects.delete?batch=1"

    headers = {
        "Host": "api.sync.so",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": '"Windows"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "trpc-accept": "application/jsonl",
        "content-type": "application/json",
        "x-sync-source": "web",
        "sec-ch-ua-mobile": "?0",
        "Accept": "*/*",
        "Origin": "https://sync.so",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://sync.so/",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate"
    }

    cookies = {
        "__Secure-sync.session_token": session_token,
        "_reb2buid": "2efd334d-05a8-49ed-97ad-9ad9495f5ca9-1748239545502",
        "__stripe_mid": "27a8a212-b84e-4739-8403-59e586330d551f555d",
        "__stripe_sid": "2b82aaf5-38b7-44bb-aa8a-d5de6f272ad958bd1e",
        "ph_phc_82dxgIiZvuUFV41LErIq8UGCNYmisHq8Fn3a4LGtsYO_posthog": "%7B%22distinct_id%22%3A%22086c0078-324f-490a-9c4b-1fff54763f47%22%2C%22%24sesid%22%3A%5B1748245709895%2C%2201970b8f-e533-7f5f-b278-dcea5ff400e1%22%2C1748245669171%5D%2C%22%24epp%22%3Atrue%7D"
    }

    data = {
        "0": {
            "json": {
                "id": project_id
            }
        }
    }

    response = requests.post(url, headers=headers, cookies=cookies, json=data)

    if response.status_code == 200:
        print("✅ Proyecto eliminado correctamente:", project_id)
        return {"success": True, "project_id": project_id}
    else:
        print(f"❌ Error al eliminar el proyecto. Código: {response.status_code}")
        print(response.text)
        return {"success": False, "error": response.text}




def stop_monitoring():
    """Función para detener manualmente el monitoreo"""
    global stop_flag
    stop_flag = True
    print("🛑 Se ha solicitado la detención del monitoreo.")

#@title proceso bucle
def monitor_generation_and_download(
    session_token: str,
    project_id: str,
    check_interval=10
):
    """
    Monitorea indefinidamente hasta encontrar el video completado.
    Se puede detener llamando a `stop_monitoring()`.
    """

    url = f"https://api.sync.so/trpc/projects.get?batch=1&input=%7B%220%22%3A%7B%22json%22%3A%7B%22id%22%3A%22{project_id}%22%7D%7D%7D"

    headers = {
        "Host": "api.sync.so",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": '"Windows"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "trpc-accept": "application/jsonl",
        "content-type": "application/json",
        "x-sync-source": "web",
        "sec-ch-ua-mobile": "?0",
        "Accept": "*/*",
        "Origin": "https://sync.so",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://sync.so/",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate"
    }

    cookies = {
        "__Secure-sync.session_token": session_token,
        "_reb2buid": "9f57ba92-2efa-4732-8ebe-91c5d82f2fa9-1748231778316",
        "_reb2bsessionID": "HZ9NKRQkGNEv55me1UzkLMEA",
        "_reb2bgeo": "%7B%22city%22%3A%22Avellaneda%22%2C%22country%22%3A%22Argentina%22%2C%22countryCode%22%3A%22AR%22%2C%22hosting%22%3Afalse%2C%22isp%22%3A%22Telefonica%20de%20Argentina%22%2C%22lat%22%3A-34.684%2C%22proxy%22%3Afalse%2C%22region%22%3A%22B%22%2C%22regionName%22%3A%22Buenos%20Aires%22%2C%22status%22%3A%22success%22%2C%22timezone%22%3A%22America%2FArgentina%2FBuenos_Aires%22%2C%22zip%22%3A%221874%22%7D",
        "ph_phc_82dxgIiZvuUFV41LErIq8UGCNYmisHq8Fn3a4LGtsYO_posthog": "%7B%22distinct_id%22%3A%22073f54a3-24b4-4fb9-b59e-7acfb63752b1%22%2C%22%24sesid%22%3A%5B1748233487190%2C%2201970abc-5e3f-78f7-9a29-a5ebdcc28e48%22%2C1748231806527%5D%2C%22%24epp%22%3Atrue%7D",
        "__stripe_mid": "4bdd337a-c921-44f7-8d1a-bf567db070b28b1bce",
        "__stripe_sid": "4d0a7720-a7d5-4570-b526-3b4fa2536c0190da43"
    }

    global stop_flag
    stop_flag = False  # Reiniciar bandera al comenzar
    attempt = 0

    while not stop_flag:
        attempt += 1
        print(f"\n🔁 Intento {attempt}: Verificando estado...")

        try:
            response = requests.get(url, headers=headers, cookies=cookies)

            if response.status_code != 200:
                print(f"❌ Error en la solicitud: Código {response.status_code}")
                print(response.text)
                time.sleep(check_interval)
                continue

            lines = response.text.strip().split('\n')
            generation_data = None

            for line in lines:
                try:
                    parsed = eval(line.replace("null", "None").replace("true", "True").replace("false", "False"))
                    if isinstance(parsed["json"], list) and len(parsed["json"]) > 2:
                        if "generations" in parsed["json"][2][0][0]:
                            project_info = parsed["json"][2][0][0]
                            generations = project_info.get("generations", [])
                            if generations:
                                generation_data = generations[0]  # Tomamos la primera generación
                            break
                except Exception as e:
                    print(f"⚠️ Error procesando línea: {e}")
                    continue

            if not generation_data:
                print("⚠️ No se encontró información de generación.")
                time.sleep(check_interval)
                continue

            status = generation_data.get("status")
            print(f"📊 Estado actual: {status}")

            if status == "COMPLETED":
                output_media_url = generation_data.get("outputMediaUrl")
                if output_media_url:
                    print("✅ Generación completada. Descargando archivo...")

                    file_name = "/tmp/output.mp4"
                    with requests.get(output_media_url, stream=True) as r:
                        r.raise_for_status()
                        with open(file_name, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                    

                    # Definir la ruta de la carpeta
                    ruta = "/content/video/"
                    # Verificar si la carpeta existe
                    if not os.path.exists(ruta):
                        # Si no existe, crearla
                        os.makedirs(ruta)
                        print(f"La carpeta ha sido creada.")
                    else:
                        print(f"La carpeta ya existe.")
                    # Recortar la franja negra
                    recortar_franja_negra("/tmp/output.mp4", "/content/video/output.mp4")

                    print("💾 Archivo guardado como: /content/video/output.mp4")

                    stop_monitoring()  # Detener bucle tras éxito
                    return file_name

                else:
                    print("❌ El campo outputMediaUrl está vacío.")
                    stop_monitoring()
                    return None

            elif status == "FAILED":
                print("❌ La generación ha fallado.")
                stop_monitoring()
                return None

            else:
                print(f"⏳ Estado: {status}. Reintentando en {check_interval} segundos...")
                time.sleep(check_interval)

        except Exception as e:
            print(f"⚠️ Error general: {e}")
            time.sleep(check_interval)

    print("🛑 Monitoreo detenido por el usuario o por finalización.")
    return None





def generate_lipsync(
    session_token: str,
    project_id: str,
    model: str,
    video_url: str,
    audio_url: str
):
  

    url = "https://api.sync.so/v2/generate"

    headers = {
        "Host": "api.sync.so",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": '"Windows"',
        "x-project-id": project_id,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "Content-Type": "application/json",
        "sec-ch-ua-mobile": "?0",
        "Accept": "*/*",
        "Origin": "https://sync.so",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://sync.so/",
        "Accept-Language": "es-ES,es;q=0.9",
        "Cookie": f"__Secure-sync.session_token={session_token}; _reb2buid=9f57ba92-2efa-4732-8ebe-91c5d82f2fa9-1748231778316; _reb2bsessionID=HZ9NKRQkGNEv55me1UzkLMEA; _reb2bgeo=%7B%22city%22%3A%22Avellaneda%22%2C%22country%22%3A%22Argentina%22%2C%22countryCode%22%3A%22AR%22%2C%22hosting%22%3Afalse%2C%22isp%22%3A%22Telefonica%20de%20Argentina%22%2C%22lat%22%3A-34.684%2C%22proxy%22%3Afalse%2C%22region%22%3A%22B%22%2C%22regionName%22%3A%22Buenos%20Aires%22%2C%22status%22%3A%22success%22%2C%22timezone%22%3A%22America%2FArgentina%2FBuenos_Aires%22%2C%22zip%22%3A%221874%22%7D; ph_phc_82dxgIiZvuUFV41LErIq8UGCNYmisHq8Fn3a4LGtsYO_posthog=%7B%22distinct_id%22%3A%22073f54a3-24b4-4fb9-b59e-7acfb63752b1%22%2C%22%24sesid%22%3A%5B1748233487190%2C%2201970abc-5e3f-78f7-9a29-a5ebdcc28e48%22%2C1748231806527%5D%2C%22%24epp%22%3Atrue%7D; __stripe_mid=4bdd337a-c921-44f7-8d1a-bf567db070b28b1bce; __stripe_sid=4d0a7720-a7d5-4570-b526-3b4fa2536c0190da43",
        "Accept-Encoding": "gzip, deflate"
    }

    data = {
        "model": model,
        "input": [
            {"type": "video", "url": video_url},
            {"type": "audio", "url": audio_url}
        ],
        "options": {
            "pads": [0, 5, 0, 0],
            "temperature": 0.5,
            "output_resolution": [1920, 1080],
            "output_format": "mp4",
            "sync_mode": "bounce",
            "active_speaker_detection": False
        }
    }

    response = requests.post(url, headers=headers, json=data)
    #print(response.text)

    # Aquí está la corrección 👇
    try:
        response_json = response.json()
    except requests.exceptions.JSONDecodeError:
        return {
            "error": True,
            "status_code": response.status_code,
            "response_text": response.text
        }

    #print(response_json)

    if response_json.get("statusCode") == 400 and "Audio exceeds duration limit" in response_json.get("message", ""):

        return {
            "error": True,
            "message": "Tu audio excede el límite permitido de 1 minuto.",
            "upgrade_link": "https://sync.so/billing/subscription"
        }
    elif response_json.get("statusCode") == 402 and "You are over your free credits limit" in response_json.get("message", ""):

        return {
            "error": True,
            "message": "Has superado el límite de créditos gratuitos.",
            "upgrade_link": "https://sync.so/billing/subscription"
        }

    if response.status_code == 201:
        return response.json()
    else:
        return {
            "error": True,
            "status_code": response.status_code,
            "response_text": response.text
        }




def upload_video_file(upload_url: str, file_path: str):
    agregar_franja_negra("/tmp/video.mp4", "/tmp/video_f.mp4")
    time.sleep(5)
    headers = {
        "Host": "prod-public-sync-user-assets.s3.us-east-1.amazonaws.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Content-Type": "audio/mpeg",
        "Origin": "https://sync.so ",
        "Referer": "https://sync.so/ ",
        "Accept-Encoding": "gzip, deflate"
    }

    with open(file_path, "rb") as f:
        data = f.read()

    response = requests.put(upload_url, headers=headers, data=data)

    if response.status_code == 200:
        print("✅ Archivo subido exitosamente.")
        return True
    else:
        print(f"❌ Error al subir archivo. Código: {response.status_code}")
        print(response.text)
        return False





def upload_audio_file(upload_url: str, file_path: str):
    headers = {
        "Host": "prod-public-sync-user-assets.s3.us-east-1.amazonaws.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Content-Type": "audio/mpeg",
        "Origin": "https://sync.so ",
        "Referer": "https://sync.so/ ",
        "Accept-Encoding": "gzip, deflate"
    }

    with open(file_path, "rb") as f:
        data = f.read()

    response = requests.put(upload_url, headers=headers, data=data)

    if response.status_code == 200:
        print("✅ Archivo subido exitosamente.")
        return True
    else:
        print(f"❌ Error al subir archivo. Código: {response.status_code}")
        print(response.text)
        return False




def generate_timestamp():
    # Devuelve el timestamp actual en segundos (10 dígitos)
    return int(time.time())

def generate_filename(prefix="audio-input-", extension=".mp3"):
    timestamp = generate_timestamp()
    return f"{prefix}{timestamp}{extension}"

def generate_mp4_filename(prefix="video-input-", extension=".mp4"):
    timestamp = generate_timestamp()
    return f"{prefix}{timestamp}{extension}"


def get_mp4upload_urls(session_token: str):
    file_name = generate_mp4_filename()  # Genera el nombre dinámico

    # Construir URL con parámetros codificados
    url = f"https://api.sync.so/trpc/fileStorage.getUploadUrl?batch=1&input=%7B%220%22%3A%7B%22json%22%3A%7B%22fileName%22%3A%22{file_name}%22%2C%22contentType%22%3A%22video%2Fmp4%22%2C%22isPublic%22%3Atrue%7D%7D%7D"

    # Headers
    headers = {
        "Host": "api.sync.so",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": '"Windows"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "trpc-accept": "application/jsonl",
        "content-type": "application/json",
        "x-sync-source": "web",
        "sec-ch-ua-mobile": "?0",
        "Accept": "*/*",
        "Origin": "https://sync.so",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://sync.so/",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate"
    }

    # Cookies
    cookies = {
        "__Secure-sync.session_token": session_token,
        "_reb2buid": "9f57ba92-2efa-4732-8ebe-91c5d82f2fa9-1748231778316",
        "_reb2bsessionID": "HZ9NKRQkGNEv55me1UzkLMEA",
        "_reb2bgeo": "%7B%22city%22%3A%22Avellaneda%22%2C%22country%22%3A%22Argentina%22%2C%22countryCode%22%3A%22AR%22%2C%22hosting%22%3Afalse%2C%22isp%22%3A%22Telefonica%20de%20Argentina%22%2C%22lat%22%3A-34.684%2C%22proxy%22%3Afalse%2C%22region%22%3A%22B%22%2C%22regionName%22%3A%22Buenos%20Aires%22%2C%22status%22%3A%22success%22%2C%22timezone%22%3A%22America%2FArgentina%2FBuenos_Aires%22%2C%22zip%22%3A%221874%22%7D",
        "ph_phc_82dxgIiZvuUFV41LErIq8UGCNYmisHq8Fn3a4LGtsYO_posthog": "%7B%22distinct_id%22%3A%22073f54a3-24b4-4fb9-b59e-7acfb63752b1%22%2C%22%24sesid%22%3A%5B1748233478121%2C%2201970abc-5e3f-78f7-9a29-a5ebdcc28e48%22%2C1748231806527%5D%2C%22%24epp%22%3Atrue%7D",
        "__stripe_mid": "4bdd337a-c921-44f7-8d1a-bf567db070b28b1bce",
        "__stripe_sid": "4d0a7720-a7d5-4570-b526-3b4fa2536c0190da43"
    }

    # Realizar la solicitud
    response = requests.get(url, headers=headers, cookies=cookies)

    #print(response.text)

    if response.status_code == 200:
        try:
            # Procesar respuesta línea por línea
            lines = response.text.strip().split('\n')
            data = {}
            for line in lines:
                json_line = line.strip()
                if json_line.startswith('{"json"'):
                    parsed = eval(json_line.replace("null", "None").replace("true", "True").replace("false", "False"))
                    if isinstance(parsed["json"], list) and len(parsed["json"]) > 2:
                        if "uploadUrl" in parsed["json"][2][0][0]:
                            data = parsed["json"][2][0][0]
                            break

            return {
                "fileName": file_name,
                "uploadUrl": data.get("uploadUrl"),
                "publicUrl": data.get("publicUrl")
            }

        except Exception as e:
            print(f"⚠️ Error al procesar la respuesta: {e}")
            return None
    else:
        print(f"❌ Error en la solicitud. Código: {response.status_code}")
        print(response.text)
        return None


def get_mp3upload_urls(session_token: str):
    file_name = generate_filename()  # Genera el nombre dinámico

    # Construir URL con parámetros codificados
    url = f"https://api.sync.so/trpc/fileStorage.getUploadUrl?batch=1&input=%7B%220%22%3A%7B%22json%22%3A%7B%22fileName%22%3A%22{file_name}%22%2C%22contentType%22%3A%22audio%2Fmpeg%22%2C%22isPublic%22%3Atrue%7D%7D%7D"

    # Headers
    headers = {
        "Host": "api.sync.so",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": '"Windows"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "trpc-accept": "application/jsonl",
        "content-type": "application/json",
        "x-sync-source": "web",
        "sec-ch-ua-mobile": "?0",
        "Accept": "*/*",
        "Origin": "https://sync.so",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://sync.so/",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate"
    }

    # Cookies
    cookies = {
        "__Secure-sync.session_token": session_token,
        "_reb2buid": "9f57ba92-2efa-4732-8ebe-91c5d82f2fa9-1748231778316",
        "_reb2bsessionID": "HZ9NKRQkGNEv55me1UzkLMEA",
        "_reb2bgeo": "%7B%22city%22%3A%22Avellaneda%22%2C%22country%22%3A%22Argentina%22%2C%22countryCode%22%3A%22AR%22%2C%22hosting%22%3Afalse%2C%22isp%22%3A%22Telefonica%20de%20Argentina%22%2C%22lat%22%3A-34.684%2C%22proxy%22%3Afalse%2C%22region%22%3A%22B%22%2C%22regionName%22%3A%22Buenos%20Aires%22%2C%22status%22%3A%22success%22%2C%22timezone%22%3A%22America%2FArgentina%2FBuenos_Aires%22%2C%22zip%22%3A%221874%22%7D",
        "ph_phc_82dxgIiZvuUFV41LErIq8UGCNYmisHq8Fn3a4LGtsYO_posthog": "%7B%22distinct_id%22%3A%22073f54a3-24b4-4fb9-b59e-7acfb63752b1%22%2C%22%24sesid%22%3A%5B1748233478121%2C%2201970abc-5e3f-78f7-9a29-a5ebdcc28e48%22%2C1748231806527%5D%2C%22%24epp%22%3Atrue%7D",
        "__stripe_mid": "4bdd337a-c921-44f7-8d1a-bf567db070b28b1bce",
        "__stripe_sid": "4d0a7720-a7d5-4570-b526-3b4fa2536c0190da43"
    }

    # Realizar la solicitud
    response = requests.get(url, headers=headers, cookies=cookies)

    #print(response.text)

    if response.status_code == 200:
        try:
            # Procesar respuesta línea por línea
            lines = response.text.strip().split('\n')
            data = {}
            for line in lines:
                json_line = line.strip()
                if json_line.startswith('{"json"'):
                    parsed = eval(json_line.replace("null", "None").replace("true", "True").replace("false", "False"))
                    if isinstance(parsed["json"], list) and len(parsed["json"]) > 2:
                        if "uploadUrl" in parsed["json"][2][0][0]:
                            data = parsed["json"][2][0][0]
                            break

            return {
                "fileName": file_name,
                "uploadUrl": data.get("uploadUrl"),
                "publicUrl": data.get("publicUrl")
            }

        except Exception as e:
            print(f"⚠️ Error al procesar la respuesta: {e}")
            return None
    else:
        print(f"❌ Error en la solicitud. Código: {response.status_code}")
        print(response.text)
        return None




def create_project(session_token: str):
    url = "https://api.sync.so/trpc/projects.create?batch=1"

    headers = {
        "Host": "api.sync.so",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": '"Windows"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "trpc-accept": "application/jsonl",
        "content-type": "application/json",
        "x-sync-source": "web",
        "sec-ch-ua-mobile": "?0",
        "Accept": "*/*",
        "Origin": "https://sync.so",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://sync.so/",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate"
    }

    cookies = {
        "__Secure-sync.session_token": session_token,
        "_reb2buid": "9f57ba92-2efa-4732-8ebe-91c5d82f2fa9-1748231778316",
        "_reb2bsessionID": "HZ9NKRQkGNEv55me1UzkLMEA",
        "_reb2bgeo": "%7B%22city%22%3A%22Avellaneda%22%2C%22country%22%3A%22Argentina%22%2C%22countryCode%22%3A%22AR%22%2C%22hosting%22%3Afalse%2C%22isp%22%3A%22Telefonica%20de%20Argentina%22%2C%22lat%22%3A-34.684%2C%22proxy%22%3Afalse%2C%22region%22%3A%22B%22%2C%22regionName%22%3A%22Buenos%20Aires%22%2C%22status%22%3A%22success%22%2C%22timezone%22%3A%22America%2FArgentina%2FBuenos_Aires%22%2C%22zip%22%3A%221874%22%7D",
        "ph_phc_82dxgIiZvuUFV41LErIq8UGCNYmisHq8Fn3a4LGtsYO_posthog": "%7B%22distinct_id%22%3A%22073f54a3-24b4-4fb9-b59e-7acfb63752b1%22%2C%22%24sesid%22%3A%5B1748233457224%2C%2201970abc-5e3f-78f7-9a29-a5ebdcc28e48%22%2C1748231806527%5D%2C%22%24epp%22%3Atrue%7D",
        "__stripe_mid": "4bdd337a-c921-44f7-8d1a-bf567db070b28b1bce",
        "__stripe_sid": "4d0a7720-a7d5-4570-b526-3b4fa2536c0190da43"
    }

    payload = {
        "0": {
            "json": {
                "mode": "CREATOR",
                "visibility": "USER"
            }
        }
    }

    response = requests.post(url, headers=headers, cookies=cookies, json=payload)

    if response.status_code == 200:
        try:
            lines = response.text.strip().split('\n')
            project_data = None
            for line in lines:
                parsed = eval(line.replace("null", "None").replace("true", "True").replace("false", "False"))
                if isinstance(parsed["json"], list) and len(parsed["json"]) > 2:
                    if "id" in parsed["json"][2][0][0]:
                        project_data = parsed["json"][2][0][0]
                        break

            if project_data:
                return {
                    "project_id": project_data.get("id"),
                    "user_id": project_data.get("userId"),
                    "organization_id": project_data.get("organizationId"),
                    "mode": project_data.get("mode"),
                    "visibility": project_data.get("visibility")
                }
            else:
                #print("❌ No se encontraron datos del proyecto en la respuesta.")
                return None
        except Exception as e:
            #print(f"⚠️ Error al procesar la respuesta: {e}")
            return None
    else:
        #print(f"❌ Error en la solicitud. Código: {response.status_code}")
        #print(response.text)
        return None


# Ejemplo de uso

def create_avatar(versions, file_mp3_path, file_mp4_path):
    session_token = os.environ.get("ACCESS_TOKEN")
    
    
    result = create_project(session_token)

    if versions == "2.0.0":
        os.environ["MODEL"] = "lipsync-2"
    elif versions == "1.9.0":
        os.environ["MODEL"]= "lipsync-1.9.0-beta"
    elif versions == "1.8.0":
        os.environ["MODEL"] = "lipsync-1.8.0"
    elif versions == "1.7.1":
        os.environ["MODEL"] = "lipsync-1.7.1"
    else:
      os.environ["MODEL"] = "lipsync-2"



    if result:
        print("✅ Proyecto creado exitosamente:")
        #print("Project ID:", result["project_id"])
        #print("User ID:", result["user_id"])
        #print("Organization ID:", result["organization_id"])
        #print("Modo:", result["mode"])
        #print("Visibilidad:", result["visibility"])
        project_id = result["project_id"]
        os.environ["PROJECT_ID"] = project_id

        if project_id:
          result_mp3 = get_mp3upload_urls(session_token)

          if result_mp3:
              print("✅ URLs obtenidas exitosamente:")
              #print("Archivo generado:", result_mp3["fileName"])
              #print("Upload URL:", result_mp3["uploadUrl"])
              #print("Public URL:", result_mp3["publicUrl"])
              url_mp3 = result_mp3["uploadUrl"]
              url_mp3_public = result_mp3["publicUrl"]

              result_mp4 = get_mp4upload_urls(session_token)

              if result_mp4:
                  print("✅ URLs obtenidas exitosamente:")
                  #print("Archivo generado:", result_mp4["fileName"])
                  #print("Upload URL:", result_mp4["uploadUrl"])
                  #print("Public URL:", result_mp4["publicUrl"])
                  url_mp4 = result_mp4["uploadUrl"]
                  url_mp4_public = result_mp4["publicUrl"]

                  success_mp3 = upload_audio_file(url_mp3, file_mp3_path)

                  if success_mp3:
                      print("🔗 Audio subido...")
                  else:
                      print("⚠️ No se pudo subir el archivo.")

                  success_mp4 = upload_video_file(url_mp4, file_mp4_path)

                  if success_mp4:
                      print("🔗 Video subido...")
                  else:
                      print("⚠️ No se pudo subir el archivo.")
                  
                  if success_mp3 and success_mp4:

                      video_url = url_mp4_public
                      audio_url = url_mp3_public
                      #print(url_mp3_public)
                      #print(url_mp4_public)

                      project_id = os.environ.get("PROJECT_ID")
                      session_token = os.environ.get("ACCESS_TOKEN")
                      model = os.environ.get("MODEL")

                      #print(session_token)
                      #print(project_id)

                      #print(model)


                      result_lip = generate_lipsync(session_token, project_id, model, url_mp4_public, url_mp3_public)

                      if not result_lip.get("error"):
                          print("✅ Generación iniciada correctamente:")
                          #print("ID de generación:", result_lip.get("id"))
                          print("Estado actual:", result_lip.get("status"))
                          #print("Código de estado:", result_lip.get("message"))
                          result_message = result_lip.get("message")
                          #print("Respuesta:", result_message)

                          # Ejemplo de ejecución local
                          if not (result_message == "Tu audio excede el límite permitido de 1 minuto.") or (result_message == "Has superado el límite de créditos gratuitos."):

                              result_file = monitor_generation_and_download(session_token, project_id)

                              if result_file:
                                  print(f"\n🎉 Archivo descargado: {result_file}")
                                  project_id = os.environ.get("PROJECT_ID")
                                  session_token = os.environ.get("ACCESS_TOKEN")

                                  result_dell = delete_project(session_token, project_id)

                                  if result_dell["success"]:
                                      print("🗑️ Proyecto borrado con éxito.")
                                      return "✅ Procesamiento de LipSync completado."
                                  else:
                                      print("⚠️ No se pudo borrar el proyecto.")
                                      return "⚠️ No se pudo borrar el proyecto."

                              else:
                                  print("\n⚠️ No se pudo obtener el archivo.")
                                  return "⚠️ No se pudo obtener el archivo."
                          else:
                              print("❌ Error:", result_message)
                              return f"❌ Error: {result_message}"


                      else:
                          print("❌ Error al iniciar la generación:")
                          print("❌ Error:", result_lip.get("message"))
                          register_lip()
                          time.sleep(1)
                          model = os.environ.get("MODEL")
                          create_avatar(model, file_mp3_path, file_mp4_path)





              else:
                  print("❌ No se pudieron obtener las URLs.")
                  return "❌ No se pudieron obtener las URLs."

          else:
              print("❌ No se pudieron obtener las URLs.")
              return "❌ No se pudieron obtener las URLs."

    else:
        print("❌ No se pudo crear el proyecto.")
        register_lip()
        time.sleep(1)
        model = os.environ.get("MODEL")
        create_avatar(model, file_mp3_path, file_mp4_path)

