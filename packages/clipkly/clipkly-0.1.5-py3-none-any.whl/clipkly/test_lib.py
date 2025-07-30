# test_clipkly.py

from clipkly.core import procesar_clips

# Ejecuta la generación de clips y Excel desde un archivo JSON
result = procesar_clips(
    archivo_json="../clips.json",            # Tu archivo de definición de clips
    video_h="../video_v.mp4",       # Ruta al video horizontal
    video_v="../video_v.mp4",         # Ruta al video vertical (opcional)
    # Offset para el video vertical (si aplica)
    offset=3.5,
    # Puedes filtrar por categoría (o dejarlo en None)
    categoria=None,
    # "muy_corto", "ideal", "largo", "muy_largo" o None
    duracion="ideal",
    # Si True, solo imprime los comandos sin ejecutarlos
    dry_run=False,
    # True para crear el .zip con los clips generados
    export_zip=True,
    out_dir="clips_generados"             # Carpeta donde guardar resultados
)

print("Clips procesados y Excel generado:", result)
