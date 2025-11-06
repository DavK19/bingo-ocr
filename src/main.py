import cv2
import numpy as np
from processor import process_image


def main():
    # Ruta de la imagen del cartón de bingo
    ruta_imagen = "carton.png"
    salida_grid = "carton_grid.png"

    # Procesar la imagen y obtener los números; además guardar la imagen con la cuadrícula
    try:
        numeros = process_image(ruta_imagen, grid=(5, 5), save_grid_path=salida_grid)
    except Exception as e:
        print(f"Error procesando la imagen: {e}")
        return

    # Mostrar rutas de archivos guardados
    print(f"Imagen con cuadrícula guardada en: {salida_grid}")
    base, ext = salida_grid.rsplit('.', 1) if '.' in salida_grid else (salida_grid, '')
    bw_path = f"{base}_bw.{ext}" if ext else f"{base}_bw"
    print(f"Imagen B/N con cuadrícula (líneas en color) guardada en: {bw_path}")
    # Imprimir los números detectados
    for fila in numeros:
        print(" | ".join(fila))


if __name__ == "__main__":
    main()