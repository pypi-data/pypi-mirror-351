import json
import pathlib
import re
import subprocess
import unicodedata
import zipfile
from datetime import datetime

import pandas as pd
from tqdm import tqdm


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"\W+", "_", text.lower())
    return re.sub(r"_+", "_", text[:40].strip("_")) or "clip"


def hhmmss_to_sec(t: str) -> float:
    dt = datetime.strptime(
        t, "%H:%M:%S.%f") if "." in t else datetime.strptime(t, "%H:%M:%S")
    return dt.hour * 3600 + dt.minute * 60 + dt.second + dt.microsecond / 1e6


def sec_to_hhmmss(seconds: float) -> str:
    s = max(0, seconds)
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    s = s % 60
    return f"{h:02}:{m:02}:{s:06.3f}"


def clasifica(segundos):
    if segundos <= 30:
        return "muy_corto"
    elif segundos <= 90:
        return "ideal"
    elif segundos <= 179:
        return "largo"
    else:
        return "muy_largo"


def procesar_clips(
    archivo_json,
    video_h=None,
    video_v=None,
    offset=0,
    categoria=None,
    duracion=None,
    dry_run=False,
    export_zip=False,
    out_dir="clips"
):
    ruta = pathlib.Path(out_dir)
    out_h = ruta / "horizontal"
    out_v = ruta / "vertical"
    out_h.mkdir(parents=True, exist_ok=True)
    out_v.mkdir(parents=True, exist_ok=True)

    with open(archivo_json, encoding="utf-8") as f:
        raw_clips = json.load(f)

    clips = [c for c in raw_clips if not categoria or c.get(
        "category") == categoria]

    if duracion:
        clips = [c for c in clips if clasifica(hhmmss_to_sec(
            c["end"]) - hhmmss_to_sec(c["start"])) == duracion]

    excel_data = []
    for i, c in enumerate(clips):
        dur = round(hhmmss_to_sec(c["end"]) - hhmmss_to_sec(c["start"]), 2)
        excel_data.append({
            "slug": c.get("slug"),
            "titulo": c.get("titulo"),
            "descripcion": c.get("descripcion", ""),
            "feeling": c.get("feeling", ""),
            "category": c.get("category", ""),
            "start": c.get("start"),
            "end": c.get("end"),
            "duracion_segundos": dur,
            "duracion_mmss": f"{int(dur // 60)}:{int(dur % 60):02}",
            "clasificacion_duracion": clasifica(dur),
            "score": c.get("score", ""),
            "tags": c.get("tags", ""),
            "quote": c.get("quote", ""),
            "kewords_detected": c.get("kewords_detected", ""),
            "personas_mencionadas": c.get("personas_mencionadas", ""),
            "actionable_tip": c.get("actionable_tip", ""),
            "thumbnail_hint": c.get("thumbnail_hint", ""),
            "platform_fit": c.get("platform_fit", ""),
            "transcript_excerpt": c.get("transcript_excerpt", ""),
            "ia_notes": c.get("ia_notes", ""),
            "fecha_publicacion": "",
            "estado": "por_publicar",
            "used_in_publication": c.get("used_in_publication", ""),
        })
    excel_path = ruta / "estado_clips.xlsx"
    pd.DataFrame(excel_data).to_excel(excel_path, index=False)

    if video_h:
        print("🎬 Procesando video horizontal...")
        for i, c in enumerate(tqdm(clips, desc="Horizontal")):
            start = hhmmss_to_sec(c["start"])
            end = hhmmss_to_sec(c["end"])
            slug = slugify(c.get("slug", f"clip_{i:02d}"))
            out = str(out_h / f"{i:02d}_{slug}.mp4").replace("\\", "/")
            cmd = f'ffmpeg -y -hide_banner -loglevel error -ss {sec_to_hhmmss(start)} -to {sec_to_hhmmss(end)} -i "{video_h}" -c copy "{out}"'
            if dry_run:
                print("[DRY RUN]", cmd)
            else:
                subprocess.run(cmd, shell=True, check=True)

    if video_v:
        print("🎬 Procesando video vertical...")
        for i, c in enumerate(tqdm(clips, desc="Vertical")):
            start = hhmmss_to_sec(c["start"]) - offset
            end = hhmmss_to_sec(c["end"]) - offset
            slug = slugify(c.get("slug", f"clip_{i:02d}"))
            out = str(out_v / f"{i:02d}_{slug}.mp4").replace("\\", "/")
            cmd = f'ffmpeg -y -hide_banner -loglevel error -ss {sec_to_hhmmss(start)} -to {sec_to_hhmmss(end)} -i "{video_v}" -c copy "{out}"'
            if dry_run:
                print("[DRY RUN]", cmd)
            else:
                subprocess.run(cmd, shell=True, check=True)

    if export_zip:
        zip_path = ruta / "clips_exportados.zip"
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for folder in [out_h, out_v]:
                for file in folder.glob("*.mp4"):
                    zipf.write(file, arcname=file.relative_to(ruta))
            zipf.write(ruta / "estado_clips.xlsx", arcname="estado_clips.xlsx")
        print("🗜️ ZIP generado:", zip_path)

    print("\n✅ ¡Listo! Clips generados.")
    print("🗂️  Excel:", ruta / "estado_clips.xlsx")
    if export_zip:
        print("📦 ZIP:", zip_path)

    return {
        "clips": clips,
        "excel": str(excel_path),
        "zip": str(zip_path) if export_zip else None
    }
