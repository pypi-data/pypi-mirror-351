import argparse

from clipkly.core import procesar_clips
from clipkly.version import __version__


def main():
    parser = argparse.ArgumentParser(description="Clipkly CLI")
    parser.add_argument("--horizontal", type=str, help="Video horizontal")
    parser.add_argument("--vertical", type=str, help="Video vertical")
    parser.add_argument("--json", type=str,
                        default="clips.json", help="Archivo JSON de clips")
    parser.add_argument("--offset", type=float, default=0.0,
                        help="Offset para vertical")
    parser.add_argument("--filter", type=str, help="Filtrar por categoría")
    parser.add_argument("--duracion", type=str, choices=[
                        "muy_corto", "ideal", "largo", "muy_largo"], help="Filtrar por duración")
    parser.add_argument("--dry-run", action="store_true", help="Solo simular")
    parser.add_argument("--zip", action="store_true",
                        help="Exportar .zip con clips")
    parser.add_argument("--out-dir", type=str,
                        default="clips", help="Directorio de salida")
    parser.add_argument("--version", "-v", action="version",
                        version=f"clipkly {__version__}")
    args = parser.parse_args()

    procesar_clips(
        archivo_json=args.json,
        video_h=args.horizontal,
        video_v=args.vertical,
        offset=args.offset,
        categoria=args.filter,
        duracion=args.duracion,
        dry_run=args.dry_run,
        export_zip=args.zip,
        out_dir=args.out_dir,
    )


if __name__ == "__main__":
    main()
