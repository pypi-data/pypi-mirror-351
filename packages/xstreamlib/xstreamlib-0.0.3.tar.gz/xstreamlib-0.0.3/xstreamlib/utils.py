"""
Funciones útiles para streaming
"""
import requests
import re



async def get_token(url, api_url):

    try:
        # Extraer chat_id y file_id de la URL de Telegram
        match = re.match(r'https://t\.me/c/(\d+)/(\d+)', url)
        if not match:
            return None
            
        chat_id, file_id = match.groups()
        
        # Preparar payload como diccionario con valores string
        payload = {
            "chat_id": str(f"-100{chat_id}"),
            "file_id": str(file_id)
        }
        
        # Obtener token con headers específicos
        headers = {
            'Content-Type': 'application/json'
        }
        # Obtener token
        token_response = requests.post(
            f"{api_url}/token",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if token_response.status_code != 200:
            return None
            
        # Parsear la respuesta JSON y extraer el token
        token_data = token_response.json()
        token = token_data.get('token')
        return token
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener el token: {str(e)}")
        return None

async def parte_streaming(url, api_url):
    """Obtiene el enlace para ver la película o serie"""

    try:

        # Construir y devolver la URL final
        token = await get_token(url)
        if not token:
            return None
        final_url = f"{api_url}/download?token={token}"
        
        return final_url

    except Exception as e:
        print(f"Error en parte_streaming: {str(e)}")
        return None
    
async def get_captions(url, api_url):
    """Obtiene los subtítulos de la película o serie"""

    try:
        caption_response = requests.get(
            f"{api_url}/get?url={url}",
            timeout=10
        )
        if caption_response.status_code != 200:
            return None 
        
        return caption_response

    except requests.exceptions.RequestException as e:
        print(f"Error al obtener los subtítulos: {str(e)}")
        return None

async def base64(url):
    """Obtiene el enlace base64 de la película o serie"""

    try:
        base64_url = base64.b64encode(url).decode('utf-8')
        return base64_url

    except Exception as e:
        print(f"Error al obtener el enlace base64: {str(e)}")
        return None
    
async def get_image(url, api_url):
    """Obtiene la imagen de la película o serie"""

    try:
        # Mandamos la url a base64
        base64_url = await base64(url)
        if not base64_url:
            return None
        
        # Construir la URL de la imagen 
        image_url = f"{api_url}/url={base64_url}"
        
        return image_url

    except Exception as e:
        print(f"Error al obtener la imagen: {str(e)}")
        return None

async def get_banner_url(url, api_url):
    """
    Obtiene la URL de la imagen de banner de un video
    """
    try:

        base64_url = await base64(url)
        if not base64_url:
            return None
        
        # Construir la URL final
        api_url = f"{api_url}img?url={base64_url}"
        return api_url
    
    except Exception as e:
        print(f"Error al obtener la URL de la imagen: {str(e)}")
        return None