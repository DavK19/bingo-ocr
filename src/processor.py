import os
import cv2
import numpy as np
import pytesseract
from preproc import preprocess_image


def process_image(image_path, grid=(5, 5), save_grid_path=None):
    """Divide la imagen en una cuadrícula, extrae texto por celda y opcionalmente guarda
    una copia de la imagen original con la cuadrícula dibujada.

    Args:
        image_path (str): ruta a la imagen de entrada.
        grid (tuple): (rows, cols) tamaño de la cuadrícula. Default (5,5).
        save_grid_path (str|None): si se provee, guarda la imagen con la cuadrícula dibujada en esa ruta.

    Returns:
        list[list[str]]: matriz de textos detectados por fila.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Imagen no encontrada: {image_path}")

    # Cargar imagen original en color y en gris
    img_color = cv2.imread(image_path)
    if img_color is None:
        raise IOError(f"No se pudo leer la imagen: {image_path}")
    img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)

    # Preprocesado global (umbral) que ya existe en preproc
    processed = preprocess_image(image_path)

    rows, cols = grid
    height, width = processed.shape
    cell_h = height // rows
    cell_w = width // cols

    # Dibujar la cuadrícula sobre una copia de la imagen original (escala apropiada)
    overlay = img_color.copy()
    # Si la imagen preprocesada tiene distinto tamaño, redimensionamos la overlay para alinear
    if (overlay.shape[0] != height) or (overlay.shape[1] != width):
        overlay = cv2.resize(overlay, (width, height), interpolation=cv2.INTER_AREA)

    line_color = (0, 0, 255)  # rojo BGR
    line_thickness = max(1, min(width, height) // 200)

    # Dibujar líneas verticales y horizontales
    for c in range(1, cols):
        x = int(c * cell_w)
        cv2.line(overlay, (x, 0), (x, height), line_color, line_thickness)
    for r in range(1, rows):
        y = int(r * cell_h)
        cv2.line(overlay, (0, y), (width, y), line_color, line_thickness)

    if save_grid_path:
        # Guardar la imagen en color con la cuadrícula (overlay)
        cv2.imwrite(save_grid_path, overlay)

    # Crear máscara global donde volcamos cada celda procesada (fondo negro, números blancos)
    full_mask = np.zeros_like(processed)

    detected = []

    # Extraer cada celda, aplicar OCR por celda
    for i in range(rows):
        row_texts = []
        for j in range(cols):
            x0 = j * cell_w
            y0 = i * cell_h
            x1 = x0 + cell_w
            y1 = y0 + cell_h

            # Añadir pequeño margen para evitar líneas de separación
            pad_x = max(2, int(cell_w * 0.05))
            pad_y = max(2, int(cell_h * 0.05))
            xa = max(0, x0 + pad_x)
            ya = max(0, y0 + pad_y)
            xb = min(width, x1 - pad_x)
            yb = min(height, y1 - pad_y)

            cell = processed[ya:yb, xa:xb]
            # Si la celda queda vacía por recortes, usar el recorte sin padding
            if cell.size == 0:
                cell = processed[y0:y1, x0:x1]

            # Opcional: mejorar la celda antes de OCR
            # Aplicar Otsu para obtener mejor binarización
            try:
                _, cell_bw = cv2.threshold(cell, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            except Exception:
                cell_bw = cell.copy()

            # --- Limpieza de ruido por celda ---
            # kernel proporcional al tamaño de la celda
            try:
                k = max(1, int(min(cell_bw.shape) / 30))
            except Exception:
                k = 1
            # kernel debe ser impar para algunos filtros; para morfologie usamos rect
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(1, k), max(1, k)))

            # Aplicar median blur si la celda es lo suficientemente grande
            try:
                if min(cell_bw.shape) >= 3:
                    cell_bw = cv2.medianBlur(cell_bw, 3)
            except Exception:
                pass

            # Apertura seguida de cierre para eliminar ruido pequeño y cerrar huecos
            try:
                cell_bw = cv2.morphologyEx(cell_bw, cv2.MORPH_OPEN, kernel)
                cell_bw = cv2.morphologyEx(cell_bw, cv2.MORPH_CLOSE, kernel)
            except Exception:
                pass

            # Eliminar componentes conectadas muy pequeñas (speckles)
            try:
                num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(cell_bw, connectivity=8)
                # área mínima: proporcional al área de la celda
                min_area = max(8, (cell_bw.shape[0] * cell_bw.shape[1]) // 500)
                cleaned = np.zeros_like(cell_bw)
                for lbl in range(1, num_labels):
                    area = stats[lbl, cv2.CC_STAT_AREA]
                    if area >= min_area:
                        cleaned[labels == lbl] = 255
                cell_bw = cleaned
            except Exception:
                pass

            # --- Cambiar fondo: floodFill desde los bordes blancos hacia el interior hasta encontrar zonas negras ---
            flood = cell_bw.copy()
            h_c, w_c = flood.shape
            # máscara para floodFill requiere tamaño (h+2, w+2)
            mask = np.zeros((h_c + 2, w_c + 2), np.uint8)

            # floodFill desde los cuatro bordes donde haya pixels blancos (255)
            # recorrer top/bottom rows
            for x in range(w_c):
                if flood[0, x] == 255:
                    cv2.floodFill(flood, mask, (x, 0), 0)
                if flood[h_c - 1, x] == 255:
                    cv2.floodFill(flood, mask, (x, h_c - 1), 0)
            # recorrer left/right cols
            for y in range(h_c):
                if flood[y, 0] == 255:
                    cv2.floodFill(flood, mask, (0, y), 0)
                if flood[y, w_c - 1] == 255:
                    cv2.floodFill(flood, mask, (w_c - 1, y), 0)

            # Ahora 'flood' tiene el fondo convertido a negro (0) hasta encontrar regiones negras
            # Asegurarnos de que los números estén en blanco (255) y el fondo en negro (0)
            white_pixels = np.count_nonzero(flood == 255)
            black_pixels = np.count_nonzero(flood == 0)
            if white_pixels < black_pixels:
                # Si hay más negro que blanco, invertir para que números queden blancos
                flood = cv2.bitwise_not(flood)

            # --- Borrar letra en la parte superior de la celda ---
            # Definir primer cuarto superior de la celda
            h_f, w_f = flood.shape
            quarter_h = max(1, int(h_f * 0.35))

            # Para OCR queremos eliminar artefactos en la parte superior: crear una copia para OCR
            flood_for_ocr = flood.copy()
            # Establecer la región superior al color de fondo (0 -> negro) para que no afecte al OCR
            flood_for_ocr[0:quarter_h, :] = 0

            # Para la máscara visual final, el usuario pidió que esa zona quede totalmente blanca;
            # creamos una copia para volcar en la máscara compuesta donde esa región será blanca (255)
            flood_for_mask = flood.copy()
            flood_for_mask[0:quarter_h, :] = 255

            # Volcar la versión para máscara en la máscara global (alineada con coordenadas de la imagen completa)
            # Asegurar límites (en caso de redondeos)
            x_end = min(width, xa + w_f)
            y_end = min(height, ya + h_f)
            full_mask[ya:y_end, xa:x_end] = flood_for_mask[0:(y_end - ya), 0:(x_end - xa)]

            # Para OCR usamos la versión flood_for_ocr invertida (números en negro sobre fondo blanco)
            ocr_img = cv2.bitwise_not(flood_for_ocr)

            try:
                text = pytesseract.image_to_string(ocr_img, config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789')
            except pytesseract.pytesseract.TesseractNotFoundError:
                raise RuntimeError("Tesseract no encontrado: asegúrate de que esté instalado y en PATH")

            row_texts.append(text.strip())
        detected.append(row_texts)

    # Después de procesar todas las celdas, si se solicitó guardar la imagen, guardar
    # la máscara compuesta (fondo negro, números blancos) con la cuadrícula dibujada
    if save_grid_path:
        base, ext = os.path.splitext(save_grid_path)
        bw_path = f"{base}_bw{ext}"
        try:
            bw_bgr = cv2.cvtColor(full_mask, cv2.COLOR_GRAY2BGR)
        except Exception:
            bw_bgr = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)

        # Dibujar la cuadrícula sobre la máscara compuesta
        for c in range(1, cols):
            x = int(c * cell_w)
            cv2.line(bw_bgr, (x, 0), (x, height), line_color, line_thickness)
        for r in range(1, rows):
            y = int(r * cell_h)
            cv2.line(bw_bgr, (0, y), (width, y), line_color, line_thickness)

        cv2.imwrite(bw_path, bw_bgr)

    return detected
    