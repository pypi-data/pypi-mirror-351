#@title verificar registro
import requests
import re
import random
import string
import uuid
import time
import os
from bs4 import BeautifulSoup
import hashlib
import json
import uuid
import urllib.parse

def get_access_token(refresh_token):
    """Obtiene el accessToken y otros datos de usuario utilizando un refreshToken.

    Args:
        refresh_token: El token refreshToken obtenido en el paso anterior.

    Returns:
        Un diccionario con accessToken, refreshToken, refreshTokenId y user, o None si falla.
    """

    url = "https://a.sync.so/token"
    headers = {
        "Host": "a.sync.so",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": "Windows",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "sec-ch-ua": "Not(A:Brand);v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
        "Content-Type": "application/json",
        "sec-ch-ua-mobile": "?0",
        "Origin": "https://sync.so",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://sync.so/",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate",

    }
    data = {"refreshToken": refresh_token}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Levantar una excepción para códigos de error HTTP

        data = response.json()

        # Extraer los datos relevantes
        access_token = data.get("accessToken")
        refresh_token = data.get("refreshToken")
        refresh_token_id = data.get("refreshTokenId")
        user_id = data["user"]["id"] #Se puede acceder directamente ya que sabemos que existe.


        return access_token, refresh_token, refresh_token_id, user_id


    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud: {e}")
        return None, None, None, None
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {e}")
        #print(f"Respuesta del servidor: {response.text}") # Imprimir la respuesta para depuración
        return None, None, None, None




def login_sync_so(email):
    url = "https://sync.so/api/auth/email-otp/send-verification-otp"

    headers = {
        "Host": "sync.so",
        "Connection": "keep-alive",
        "sentry-trace": "eeefa480e668450ba27845a9f215751a-93998414a910a331-1",
        "sec-ch-ua-platform": '"Windows"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "content-type": "application/json",
        "sec-ch-ua-mobile": "?0",
        "baggage": "sentry-environment=production,sentry-release=5RzXWqE60NFCCNw5zBvfd,sentry-public_key=ae5c877441c3c02186a92764c98c688f,sentry-trace_id=eeefa480e668450ba27845a9f215751a,sentry-sample_rate=1,sentry-sampled=true",
        "Accept": "*/*",
        "Origin": "https://sync.so",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://sync.so/signup",
        "Accept-Language": "es-ES,es;q=0.9",
        #"Cookie": '_reb2buid=9f57ba92-2efa-4732-8ebe-91c5d82f2fa9-1748231778316; _reb2bsessionID=HZ9NKRQkGNEv55me1UzkLMEA; _reb2bgeo=%7B%22city%22%3A%22Avellaneda%22%2C%22country%22%3A%22Argentina%22%2C%22countryCode%22%3A%22AR%22%2C%22hosting%22%3Afalse%2C%22isp%22%3A%22Telefonica%20de%20Argentina%22%2C%22lat%22%3A-34.684%2C%22proxy%22%3Afalse%2C%22region%22%3A%22B%22%2C%22regionName%22%3A%22Buenos%20Aires%22%2C%22status%22%3A%22success%22%2C%22timezone%22%3A%22America%2FArgentina%2FBuenos_Aires%22%2C%22zip%22%3A%221874%22%7D; ph_phc_82dxgIiZvuUFV41LErIq8UGCNYmisHq8Fn3a4LGtsYO_posthog=%7B%22distinct_id%22%3A%2201970abc-5e41-7866-81f9-74080b0a98ad%22%2C%22%24sesid%22%3A%5B1748231809788%2C%2201970abc-5e3f-78f7-9a29-a5ebdcc28e48%22%2C1748231806527%5D%7D',
        "Accept-Encoding": "gzip, deflate"
    }

    data = {
        "email": email,
        "type": "sign-in"
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        try:
            json_response = response.json()
            if json_response.get("success"):
                print("✅ Solicitud exitosa: 'success' es True")
                return "Success"
            else:
                print("❌ 'success' no es True:", json_response)
                return "Error"
        except Exception as e:
            print("⚠️ No se pudo decodificar la respuesta JSON:", e)
            return "Error json"
    else:
        print(f"❌ Error en la solicitud. Código de estado: {response.status_code}")
        return "Error code"



def get_refresh_token(email, otp):
    url = "https://sync.so/api/auth/sign-in/email-otp"

    headers = {
        "Host": "sync.so",
        "Connection": "keep-alive",
        "sentry-trace": "30f715bb17bc4a43ab31814661fbda0a-9782c72c07b888f2-1",
        "sec-ch-ua-platform": '"Windows"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "content-type": "application/json",
        "sec-ch-ua-mobile": "?0",
        "baggage": "sentry-environment=production,sentry-release=5RzXWqE60NFCCNw5zBvfd,sentry-public_key=ae5c877441c3c02186a92764c98c688f,sentry-trace_id=30f715bb17bc4a43ab31814661fbda0a,sentry-sample_rate=1,sentry-sampled=true",
        "Accept": "*/*",
        "Origin": "https://sync.so",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": f"https://sync.so/verify-otp?email={email}",
        "Accept-Language": "es-ES,es;q=0.9",
        "Cookie": '_reb2buid=9f57ba92-2efa-4732-8ebe-91c5d82f2fa9-1748231778316; _reb2bsessionID=HZ9NKRQkGNEv55me1UzkLMEA; _reb2bgeo=%7B%22city%22%3A%22Avellaneda%22%2C%22country%22%3A%22Argentina%22%2C%22countryCode%22%3A%22AR%22%2C%22hosting%22%3Afalse%2C%22isp%22%3A%22Telefonica%20de%20Argentina%22%2C%22lat%22%3A-34.684%2C%22proxy%22%3Afalse%2C%22region%22%3A%22B%22%2C%22regionName%22%3A%22Buenos%20Aires%22%2C%22status%22%3A%22success%22%2C%22timezone%22%3A%22America%2FArgentina%2FBuenos_Aires%22%2C%22zip%22%3A%221874%22%7D; ph_phc_82dxgIiZvuUFV41LErIq8UGCNYmisHq8Fn3a4LGtsYO_posthog=%7B%22distinct_id%22%3A%2201970abc-5e41-7866-81f9-74080b0a98ad%22%2C%22%24sesid%22%3A%5B1748231822864%2C%2201970abc-5e3f-78f7-9a29-a5ebdcc28e48%22%2C1748231806527%5D%7D',
        "Accept-Encoding": "gzip, deflate"
    }

    payload = {
        "email": email,
        "otp": otp
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            data = response.json()

            # Extraer __Secure-sync.session_token del header Set-Cookie
            set_cookie_header = response.headers.get('Set-Cookie', '')
            session_token = None
            if set_cookie_header:
                match = re.search(r"__Secure-sync\.session_token=([^;]+)", set_cookie_header)
                if match:
                    session_token = match.group(1)

            return {
                "token": data.get("token"),
                "user_id": data["user"].get("id"),
                "email": data["user"].get("email"),
                "session_token": session_token
            }
        except Exception as e:
            print("⚠️ Error al procesar la respuesta:", e)
            return None
    else:
        print(f"❌ Error: Código de estado {response.status_code}")
        print(response.text)
        return None




def extract_sync_so_url(html_content):

    """
    Extrae el código de verificación del HTML proporcionado.

    Args:
        html_content (str): Contenido HTML donde buscar el código.

    Returns:
        str: El código encontrado, o None si no se encuentra.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Buscar el párrafo que contiene los span con números
    code_container = soup.find("p", style=lambda value: value and "letter-spacing" in value)

    if code_container:
        digits = [span.get_text(strip=True) for span in code_container.find_all("span")]
        return ''.join(digits)

    return None

# Función para convertir la contraseña en MD5
def convertir_a_md5(texto):
    return hashlib.md5(texto.encode('utf-8')).hexdigest()

# Función para registrar el usuario
def registrar_usuario(password, ticket, username):
    url = "https://app.jogg.ai/edge-service/v1/auth/register"
    headers = {
        "Host": "app.jogg.ai",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": "Windows",
        "X-APP-ID": "52002",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "sec-ch-ua": "Not(A:Brand;v=99, Google Chrome;v=133, Chromium;v=133)",
        "Content-Type": "application/json",
        "sec-ch-ua-mobile": "?0",
        "Origin": "https://app.jogg.ai",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://app.jogg.ai/register",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate"
    }

    # Convertir la contraseña a MD5
    password_md5 = convertir_a_md5(password)

    # Datos a enviar en la solicitud POST
    data = {
        "action": "reg",
        "appid": 52000,
        "password": password_md5,
        "ticket": ticket,
        "username": username
    }

    response = requests.post(url, json=data, headers=headers)

    try:
        respuesta_json = response.json()
        msg = respuesta_json.get("msg", "")
        token = respuesta_json.get("data", {}).get("token", None)

        # Validar si el msg es "success"
        if msg == "success":
            return token
        else:
            return None  # Si no es success, retornar None

    except requests.exceptions.JSONDecodeError:
        return None  # Si hay un error en la respuesta, retornar None



def verificar_codigo(ticket, username, code):
    url = "https://app.jogg.ai/edge-service/v1/auth/check_code"
    headers = {
        "X-APP-ID": "52002",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://app.jogg.ai",
        "Referer": "https://app.jogg.ai/register",
    }
    data = {
        "ticket": ticket,
        "username": username,
        "action": "reg",
        "code": code
    }

    response = requests.post(url, json=data, headers=headers)

    # Convertir la respuesta a JSON
    try:
        respuesta_json = response.json()
        msg = respuesta_json.get("msg", "")
        nuevo_ticket = respuesta_json.get("data", {}).get("ticket", None)

        # Validar si msg es "success"
        if msg == "success":
            return nuevo_ticket
        else:
            return None  # Retorna None si no es "success"

    except requests.exceptions.JSONDecodeError:
        return None  # Retorna None si hay un error en la respuesta




def enviar_codigo(correo):
    url = "https://app.jogg.ai/edge-service/v1/auth/send_code"
    headers = {
        "X-APP-ID": "52002",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://app.jogg.ai",
        "Referer": "https://app.jogg.ai/register",
    }
    data = {
        "username": correo,
        "action": "reg",
        "appid": 52000
    }

    response = requests.post(url, json=data, headers=headers)

    # Convertir la respuesta a JSON
    try:
        respuesta_json = response.json()
        msg = respuesta_json.get("msg", "")
        ticket = respuesta_json.get("data", {}).get("ticket", None)

        # Validar si msg es "success"
        if msg == "success":
            return ticket
        else:
            return None  # Retorna None si no es "success"

    except requests.exceptions.JSONDecodeError:
        return None  # Retorna None si hay un error en la respuesta





COMMON_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9',
    'Accept-Encoding': 'gzip, deflate'
}

def extraer_dominios(response_text):
    """Extrae dominios de un texto utilizando expresiones regulares."""
    dominios = re.findall(r'id="([^"]+\.[^"]+)"', response_text)
    return dominios

def extraer_codigo(html):
    soup = BeautifulSoup(html, "html.parser")

    # Buscar el código en un párrafo con estilo específico
    codigo_tag = soup.find("p", style="margin: 30px 0; font-size: 24px")
    if codigo_tag:
        return codigo_tag.text.strip()

    # Si el código no se encuentra en el estilo esperado, buscar con regex
    codigo_match = re.search(r"\b\d{6}\b", soup.get_text())
    if codigo_match:
        return codigo_match.group()

    return None  # Retorna None si no encuentra el código


def delete_temp_mail(username_email, dominios_dropdown, extracted_string):
    """Borra el correo temporal especificado."""
    EMAIL_FAKE_URL = 'https://email-fake.com/'
    url = f"{EMAIL_FAKE_URL}/del_mail.php"

    headers = {
        'Host': 'email-fake.com',
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
        'Origin': 'https://email-fake.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Language': 'es-ES,es;q=0.9',
        'Cookie': f'embx=%5B%22{username_email}%40{dominios_dropdown}%22%2C',
    }

    data = f'delll={extracted_string}'

    response = requests.post(url, headers=headers, data=data)

    if "Message deleted successfully" in response.text:
        print("Temporary mail deleted...")
        return True
    else:
        print("Error deleting temporary email...")
        return False

def generar_contrasena():
    """Genera una contraseña aleatoria."""
    caracteres = string.ascii_letters + "0123456789" + "#$%&/()@_-*+[]"
    longitud = 10
    contraseña = ''.join(random.choice(caracteres) for _ in range(longitud))
    return contraseña

def enviar_formulario(url, datos):
    """Envía una solicitud POST a un formulario web."""
    response = requests.post(url, data=datos)
    return response

def obtener_sitio_web_aleatorio(response_text):
    """Obtiene un sitio web aleatorio de los dominios extraídos."""
    dominios = extraer_dominios(response_text)
    sitio_web_aleatorio = random.choice(dominios)
    return sitio_web_aleatorio

def generar_nombre_completo():
    """Genera un nombre completo triplicando el nombre y apellido, junto con un número aleatorio de 3 dígitos."""
    nombres = ["Juan", "Pedro", "Maria", "Ana", "Luis", "Sofia", "Diego", "Laura", "Javier", "Isabel",
               "Pablo", "Marta", "David", "Elena", "Sergio", "Irene", "Daniel", "Alicia", "Carlos", "Sandra",
               "Antonio", "Lucia", "Miguel", "Sara", "Jose", "Cristina", "Alberto", "Blanca", "Alejandro", "Marta",
               "Francisco", "Esther", "Roberto", "Silvia", "Manuel", "Patricia", "Marcos", "Victoria", "Fernando", "Rosa",
               # Nombres comunes de EE.UU.
               "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Charles", "Thomas",
               "Christopher", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua",
               "Kenneth", "Kevin", "Brian", "George", "Edward", "Ronald", "Timothy", "Jason", "Jeffrey", "Ryan",
               "Jacob", "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon",
               "Benjamin", "Samuel", "Frank", "Gregory", "Raymond", "Alexander", "Patrick", "Jack", "Dennis", "Jerry",
               "Tyler", "Aaron", "Henry", "Douglas", "Jose", "Peter", "Adam", "Zachary", "Nathan", "Walter",
               "Kyle", "Harold", "Carl", "Arthur", "Gerald", "Roger", "Keith", "Jeremy", "Terry", "Lawrence",
               "Sean", "Christian", "Ethan", "Austin", "Joe", "Jordan", "Albert", "Jesse", "Willie", "Billy"]

    apellidos = ["Garcia", "Rodriguez", "Gonzalez", "Fernandez", "Lopez", "Martinez", "Sanchez", "Perez", "Alonso", "Diaz",
                 "Martin", "Ruiz", "Hernandez", "Jimenez", "Torres", "Moreno", "Gomez", "Romero", "Alvarez", "Vazquez",
                 "Gil", "Lopez", "Ramirez", "Santos", "Castro", "Suarez", "Munoz", "Gomez", "Gonzalez", "Navarro",
                 "Dominguez", "Lopez", "Rodriguez", "Sanchez", "Perez", "Garcia", "Gonzalez", "Martinez", "Fernandez", "Lopez",
                 # Apellidos comunes de EE.UU.
                 "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                 "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
                 "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
                 "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
                 "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
                 "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes",
                 "Stewart", "Morris", "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper",
                 "Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ward", "Cox", "Diaz", "Richardson", "Wood"]


    nombre = random.choice(nombres)
    apellido = random.choice(apellidos)
    numero = random.randint(100, 999)

    nombre_completo = f"{nombre}_{apellido}_{numero}"
    return nombre_completo.lower()

def get_verification_code(username_email, dominios_dropdown):
    """Obtiene el código de verificación del correo y el identificador."""
    EMAIL_FAKE_URL = 'https://email-fake.com'
    url = f"{EMAIL_FAKE_URL}/"

    headers = {
        'Host': 'email-fake.com',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        **COMMON_HEADERS,
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': 'Windows',
        'Cookie': f'surl={dominios_dropdown}%2F{username_email}',
    }

    response = requests.get(url, headers=headers)

    #print(response.text)

    verification_code = extract_sync_so_url(response.text)
    #print(verification_code)

    # Utiliza una expresión regular para encontrar el identificador largo
    identifier_match = re.search(r'delll:\s*"([a-zA-Z0-9]+)"', response.text)

    # Extrae y retorna los valores si fueron encontrados
    if verification_code and identifier_match:
        #verification_code = verification_code_match.group(1)
        identifier = identifier_match.group(1)
        return verification_code, identifier
    else:
        return None, None


def iniciar_sesion(username, password):
    url = "https://app-api.pixverse.ai/creative_platform/login"

    headers = {
        "Host": "app-api.pixverse.ai",
        "Connection": "keep-alive",
        "X-Platform": "Web",
        "sec-ch-ua-platform": "\"Windows\"",
        "Accept-Language": "es-ES",
        "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
        "sec-ch-ua-mobile": "?0",
        "Ai-Trace-Id": str(uuid.uuid4()),  # Genera un nuevo Ai-Trace-Id dinámico
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://app.pixverse.ai",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://app.pixverse.ai/",
        "Accept-Encoding": "gzip, deflate"
    }

    payload = {
        "Username": username,
        "Password": password
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Lanza un error si el código de estado no es 2xx

        data = response.json()


        # Extraer el token si existe
        if "Resp" in data and "Result" in data["Resp"] and "Token" in data["Resp"]["Result"]:
            return data["Resp"]["Result"]["Token"]
        else:
            return None  # Retorna None si no se encuentra el token

    except requests.RequestException as e:
        #print("Error en la solicitud:", e)
        return None

def solicitar_verificacion(mail, username, password):
    # Solicitar datos al usuario

    # URL del endpoint
    url = "https://app-api.pixverse.ai/app/v1/account/getVerificationCode"

    # Headers de la solicitud
    headers = {
        "user-agent": "PixVerse 1.5.7 /(Android 9;2304FPN6DG)",
        "ai-trace-id": str(uuid.uuid4()),  # Genera un nuevo Ai-Trace-Id dinámico
        "accept-language": "en-US",
        "accept-encoding": "gzip",
        "content-length": "84",
        "x-device-id": "4fa8c75370c89711155735e73ec78d8eab5a3288",
        "host": "app-api.pixverse.ai",
        "content-type": "application/json",
        "x-app-version": "1.5.7",
        "x-platform": "Android",
        "token": ""  # Aquí deberías agregar el token si lo tienes
    }

    # Cuerpo de la solicitud (payload) con los datos ingresados por el usuario
    payload = {
        "Mail": mail,
        "Username": username,
        "Password": password
    }

    # Realizar la solicitud POST
    response = requests.post(url, headers=headers, json=payload)
    #print(response.text)
    #print(response.status_code)

    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        response_data = response.json()
        if response_data.get("ErrMsg") == "Success":
            print("✅ La solicitud fue exitosa.")
            #print("Respuesta completa:", response_data)
            return "✅ La solicitud fue exitosa."
        else:
            print("❌ La solicitud no fue exitosa. Mensaje de error:", response_data.get("ErrMsg"))
            return "This username is already taken."
    else:
        print("❌ Error en la solicitud. Código de estado:", c)
        return "This username is already taken."


def create_email(min_name_length=10, max_name_length=10):
    url = "https://api.internal.temp-mail.io/api/v3/email/new"
    headers = {
        "Host": "api.internal.temp-mail.io",
        "Connection": "keep-alive",
        "Application-Name": "web",
        "sec-ch-ua-platform": "\"Windows\"",
        "Application-Version": "3.0.0",
        "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://temp-mail.io",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://temp-mail.io/",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate"
    }
    data = {
        "min_name_length": min_name_length,
        "max_name_length": max_name_length
    }

    # Hacer la solicitud
    response = requests.post(url, json=data, headers=headers)

    # Extraer el email de la respuesta JSON
    if response.status_code == 200:
        email = response.json().get("email")
        return email
    else:
        return None


def extract_code_from_text(body_text):
    # Buscar un patrón de 6 dígitos en el texto
    match = re.search(r'\b\d{6}\b', body_text)
    if match:
        return match.group(0)
    return None

def check_code_with_retries(username_email, dominios_dropdown, retries=6, delay=10):
    for attempt in range(retries):
        print(f"Intento {attempt + 1} de {retries}...")
        code, identifier = get_verification_code(username_email, dominios_dropdown)
        if code:
            print(f"Código de verificación...")
            delete_temp_mail(username_email, dominios_dropdown, identifier)
            return code
        #print("Código no encontrado. Esperando 10 segundos antes de reintentar...")
        time.sleep(delay)
    print("Se alcanzó el máximo de intentos sin éxito.")
    return None

def guardar_credenciales(username, password):
    """
    Guarda las credenciales en un archivo de texto sin sobrescribir las anteriores.
    """
    ruta_archivo = "/content/cuenta.txt"
    with open(ruta_archivo, "a") as archivo:
        archivo.write(f"{username}:{password}\n")
    print(f"📂 Credenciales guardadas...")

# Ejemplo de uso
def register_lip():
    """
    Función generadora que registra un usuario y envía actualizaciones en tiempo real.
    """
    password_segura = generar_contrasena()
    url = 'https://email-fake.com/'
    # Supongamos que el formulario en el sitio web tiene un campo llamado 'campo_correo'
    datos = {'campo_correo': 'ejemplo@dominio.com'}
    # Enviar la solicitud POST al formulario
    response = enviar_formulario(url, datos)
    # Obtener un sitio web aleatorio de los dominios extraídos
    sitio_domain = obtener_sitio_web_aleatorio(response.text)
    # Generar y mostrar un nombre completo
    nombre_completo = generar_nombre_completo()
    time.sleep(3)
    # Llamar a la función con valores personalizados
    correo = f'{nombre_completo}@{sitio_domain}'
    username = nombre_completo
    password = password_segura
    email = correo

    #print(correo)
    #print(username)
    #print(password)

    # Ejemplo de uso en Google Colab:
    success = login_sync_so(correo)

    if success == "Success":
      print("Solicitud exitosa. Revisa tu correo electrónico para completar el inicio de sesión.")
      #print(f"Detalles de la respuesta: {response.text}")

      # Esperar y obtener el código de verificación
      print("⏳ Esperando el código de verificación...\n")
      time.sleep(2)
      verification_code = check_code_with_retries(nombre_completo, sitio_domain)

      if verification_code:
          print(f"✅ Código de verificación recibido: ******\n")

          result = get_refresh_token(correo, verification_code)
          if result:
              print("✅ Inicio de sesión exitoso:")
              #print("Token:", result["token"])
              #print("User ID:", result["user_id"])
              #print("Email:", result["email"])
              #print("Session Token:", result["session_token"])
              session_token = result["session_token"]
              token = result["token"]
              user_id = result["user_id"]
              os.environ["ACCESS_TOKEN"] = session_token
              os.environ["TOKEN"] = token
              os.environ["USER_ID"] = user_id
              os.environ["REG"] = "REGISTRO"


          else:
              print("❌ Fallo en la verificación del OTP")
              register_lip()

      else:
          print("❌ No se pudo obtener el código de verificación.\n")
          register_lip()
          return

    else:
      print("❌ No se pudo registrar el usuario.\n")
      register_lip()  # Llamada recursiva para generar un nuevo usuario

