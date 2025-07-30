# XStreamLib

Una biblioteca Python moderna y fácil de usar para interactuar con la API de Udyat. Diseñada para ser flexible, robusta y permitir configuración personalizada de la URL de la API.

## ✨ Características

- 🚀 **Fácil de usar**: API intuitiva y bien documentada
- 🔒 **Manejo robusto de errores**: Excepciones personalizadas con información detallada
- 📁 **Subida de archivos**: Soporte nativo para multimedia
- 📦 **Context managers**: Gestión automática de recursos
- 🎯 **Type hints**: Completamente tipado para mejor experiencia de desarrollo
- 🔧 **Endpoints personalizados**: Flexibilidad total para cualquier API

## 🚀 Instalación

### Instalación básica

```bash
pip install xstreamlib
```

### 📖 Ejemplo básico
```python
import asyncio
from xstreamlib.stream import Stream

async def main():
    # Ejemplo de uso de la biblioteca
    # Crear instancia de Stream con la URL base de la API
    stream = Stream("https://api.ejemplo.com")
    
    # URL del contenido de ejemplo
    url = "https://t.me/c/1234567890/123"
    
    # Obtener URL de streaming
    stream_url = await stream.get_stream_url(url)
    if stream_url:
        print(f"URL de streaming: {stream_url}")
    
    # Obtener subtítulos
    subtitles = await stream.get_subtitles(url)
    if subtitles:
        print(f"Subtítulos disponibles: {subtitles}")
    
    # Obtener miniatura
    thumbnail = await stream.get_thumbnail(url)
    if thumbnail:
        print(f"URL de miniatura: {thumbnail}")
    
    # Obtener banner
    banner = await stream.get_banner(url)
    if banner:
        print(f"URL de banner: {banner}")

if __name__ == "__main__":
    # Ejecutar el ejemplo
    asyncio.run(main())
```

### Tipos de errores comunes

- **400 Bad Request**: Parámetros inválidos
- **500 Internal Server Error**: Error del servidor

## 🆘 Soporte

- 📖 [Documentación](https://xstreamlib.readthedocs.io/)
- 🐛 [Issues](https://github.com/yourusername/xstreamlib/issues)
- 💬 [Discusiones](https://github.com/yourusername/xstreamlib/discussions)

### Próximas versiones

- [ ] **v0.0.2**: Mejoras

### Características futuras

- [ ] Métricas y monitoréo para limitar las peticiones 

## 🏆 Reconocimientos

- Agradecimientos al creador de la api mi grandioso padre
- Facilidad para obtener enlaces directos de telegram.
- Construido con amor para la comunidad de desarrolladores Python.

---

**¿Te gusta xstreamlib?** ¡Dale una ⭐ en GitHub y compártelo con otros desarrolladores!