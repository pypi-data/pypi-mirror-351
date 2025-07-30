# 🎬 clipkly

`clipkly` es una herramienta CLI para developers, creadores técnicos y equipos de contenido que quieren extraer los mejores momentos de un video horizontal o vertical sin perder tiempo.

Le das un `.json` con los momentos clave (puedes generarlos desde los subtítulos), y te devuelve:

- Clips recortados con precisión quirúrgica (gracias a FFmpeg)

- Un archivo .xlsx con metadatos listos para planificar publicaciones

- Una estructura de carpetas clara para organizar horizontal vs. vertical

¿Usas Twitch, YouTube o TikTok?
¿Subes contenido técnico, educativo o de comunidad?
Entonces clipkly es tu nuevo asistente para postproducción.

---

## 🚀 Instalación

```bash
pip install clipkly
```

## ⚡ Uso básico
```bash
clipkly --vertical video_v.mp4 --offset 403.025 --json clips.json
```
También puedes incluir la versión horizontal:
```bash	
clipkly --horizontal video_h.mp4 --vertical video_v.mp4 --offset 403.025
```

## 📁 Resultado
Se generarán clips automáticamente en:

```css
clips/
├── horizontal/    ← Clips del video horizontal (sin offset)
├── vertical/      ← Clips del video vertical (con offset)
└── estado_clips.xlsx  ← Metadatos editoriales en Excel
```

## 🧾 Formato del archivo `clips.json`

```json
[
  {
    "start": "01:46:31.760",
    "end": "01:47:17.199",
    "slug": "titulo_del_clip",
    "titulo": "Título optimizado para SEO",
    "descripcion": "Descripción breve del contenido",
    "feeling": "emocion o tono del clip",
    "category": "categoría del clip"
  }
]
```
## 🧩 Argumentos disponibles

| Argumento          | Descripción                                                      |
| ------------------ | ---------------------------------------------------------------- |
| `--offset`         | Desfase (en segundos) aplicado solo al video vertical            |
| `--horizontal`     | Ruta al archivo horizontal (opcional)                            |
| `--vertical`       | Ruta al archivo vertical (opcional)                              |
| `--json`           | Ruta al archivo JSON con los clips (default: `clips.json`)       |
| `--filter`         | Filtrar por categoría (inspiracional, educativo, etc)            |
| `--duracion`       | Filtrar por duración: `muy_corto`, `ideal`, `largo`, `muy_largo` |
| `--dry-run`        | Muestra lo que se haría sin ejecutar FFmpeg                      |
| `--out-dir`        | Directorio de salida para los clips (default: `clips/`)          |
| `--zip`            | Comprime los clips en un archivo ZIP al finalizar                |
| `--version` / `-v` | Muestra la versión instalada                                     |
| `--help` / `-h`    | Muestra la ayuda de uso                                          |


## 🧾 Excel generado



## 🙌 Créditos

Este proyecto fue creado por **Julian Dario Luna Patiño**, ingeniero de software, arquitecto de soluciones en la nube y creador de contenido en [TryCatch.tv](https://trycatch.tv).

**clipkly** nació como una herramienta práctica para automatizar la creación de clips a partir de transmisiones en vivo, especialmente útil para quienes trabajan con contenido en plataformas como YouTube, TikTok e Instagram.

📫 Contacto: [judlup@trycatch.tv](mailto:judlup@trycatch.tv)

✨ Dedicado con cariño a **Nikol Daniela** ❤️
