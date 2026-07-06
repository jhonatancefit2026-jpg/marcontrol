"""
Genera el favicon de MarControl usando Pillow.
Icono de pez estilizado en color azul marino.
"""
from PIL import Image, ImageDraw, ImageFont
import os


def generar_favicon(ruta_salida="assets/favicon.ico"):
    """Genera un favicon profesional para la aplicación MarControl."""
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)

    tamanos = [16, 32, 48, 64, 128, 256]
    imagenes = []

    for tam in tamanos:
        img = Image.new("RGBA", (tam, tam), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Fondo círculo azul marino
        margen = max(1, tam // 10)
        draw.ellipse([margen, margen, tam - margen, tam - margen],
                     fill=(26, 59, 187, 255))

        # Cuerpo del pez (elipse principal)
        cx, cy = tam // 2, tam // 2
        rx = int(tam * 0.28)
        ry = int(tam * 0.18)
        draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry],
                     fill=(255, 255, 255, 230))

        # Cola (triángulo a la izquierda)
        cola_x = cx - rx
        cola_pts = [
            (cola_x, cy),
            (cola_x - int(tam * 0.18), cy - int(tam * 0.18)),
            (cola_x - int(tam * 0.18), cy + int(tam * 0.18)),
        ]
        draw.polygon(cola_pts, fill=(255, 255, 255, 200))

        # Ojo
        ojo_x = cx + int(rx * 0.5)
        ojo_r = max(1, int(tam * 0.06))
        draw.ellipse([ojo_x - ojo_r, cy - ojo_r, ojo_x + ojo_r, cy + ojo_r],
                     fill=(26, 59, 187, 255))

        # Aleta dorsal (pequeño triángulo arriba)
        aleta_pts = [
            (cx, cy - ry),
            (cx - int(tam * 0.1), cy - ry - int(tam * 0.12)),
            (cx + int(tam * 0.05), cy - ry),
        ]
        draw.polygon(aleta_pts, fill=(255, 255, 255, 200))

        imagenes.append(img)

    # Guardar como .ico con múltiples tamaños
    imagenes[0].save(
        ruta_salida,
        format="ICO",
        sizes=[(t, t) for t in tamanos],
        append_images=imagenes[1:]
    )
    print(f"[Favicon] Generado en: {ruta_salida}")
    return ruta_salida


if __name__ == "__main__":
    generar_favicon()
