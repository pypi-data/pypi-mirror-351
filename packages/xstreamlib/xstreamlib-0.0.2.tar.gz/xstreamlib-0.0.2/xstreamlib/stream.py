"""
Esta es la documentación del módulo stream.
Proporciona la clase principal Stream para manejar contenido multimedia.
"""
from .utils import parte_streaming, get_captions, get_image, get_banner_url

class Stream:
    """
    Clase que representa un gestor de streaming de contenido multimedia.
    
    Attributes:
        api_url (str): URL base de la API
    """
    
    def __init__(self, api_url: str):
        """
        Inicializa un nuevo gestor de streaming.
        
        Args:
            api_url (str): URL base de la API
        """
        self.api_url = api_url
        
    async def get_stream_url(self, url: str) -> str:
        """
        Obtiene la URL de streaming del contenido.
        
        Args:
            url (str): URL de Telegram del contenido
            
        Returns:
            str: URL de streaming o None si hay error
        """
        if not url:
            return None
        return await parte_streaming(url, self.api_url)
    
    async def get_subtitles(self, url: str) -> dict:
        """
        Obtiene los subtítulos del contenido.
        
        Args:
            url (str): URL de Telegram del contenido
            
        Returns:
            dict: Respuesta con los subtítulos o None si hay error
        """
        if not url:
            return None
        return await get_captions(url, self.api_url)
    
    async def get_thumbnail(self, url: str) -> str:
        """
        Obtiene la URL de la miniatura del contenido.
        
        Args:
            url (str): URL de Telegram del contenido
            
        Returns:
            str: URL de la imagen o None si hay error
        """
        if not url:
            return None
        return await get_image(url, self.api_url)
    
    async def get_banner(self, url: str) -> str:
        """
        Obtiene la URL del banner del contenido.
        
        Args:
            url (str): URL de Telegram del contenido
            
        Returns:
            str: URL del banner o None si hay error
        """
        if not url:
            return None
        return await get_banner_url(url, self.api_url)