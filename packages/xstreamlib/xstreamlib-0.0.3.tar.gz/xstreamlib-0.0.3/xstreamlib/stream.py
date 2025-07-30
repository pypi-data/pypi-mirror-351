"""
Esta es la documentación del módulo stream.
Proporciona la clase principal Stream para manejar contenido multimedia.
"""
from .utils import parte_streaming, get_captions, get_image, get_banner_url

class Stream:
    """
    Clase que representa un gestor de streaming de contenido multimedia.
    """
    
    @staticmethod
    async def get_stream_url(url: str, api_url: str) -> str:
        """
        Obtiene la URL de streaming del contenido.
        
        Args:
            url (str): URL de Telegram del contenido
            api_url (str): URL base de la API
            
        Returns:
            str: URL de streaming o None si hay error
        """
        if not url or not api_url:
            return None
        return await parte_streaming(url, api_url)
    
    @staticmethod
    async def get_subtitles(url: str, api_url: str) -> dict:
        """
        Obtiene los subtítulos del contenido.
        
        Args:
            url (str): URL de Telegram del contenido
            api_url (str): URL base de la API
            
        Returns:
            dict: Respuesta con los subtítulos o None si hay error
        """
        if not url or not api_url:
            return None
        return await get_captions(url, api_url)
    
    @staticmethod
    async def get_thumbnail(url: str, api_url: str) -> str:
        """
        Obtiene la URL de la miniatura del contenido.
        
        Args:
            url (str): URL de Telegram del contenido
            api_url (str): URL base de la API
            
        Returns:
            str: URL de la imagen o None si hay error
        """
        if not url or not api_url:
            return None
        return await get_image(url, api_url)
    
    @staticmethod
    async def get_banner(url: str, api_url: str) -> str:
        """
        Obtiene la URL del banner del contenido.
        
        Args:
            url (str): URL de Telegram del contenido
            api_url (str): URL base de la API
            
        Returns:
            str: URL del banner o None si hay error
        """
        if not url or not api_url:
            return None
        return await get_banner_url(url, api_url)