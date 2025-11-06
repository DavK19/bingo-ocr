import cv2
import numpy as np

def preprocess_image(image_path):
    # Cargar imagen y convertir a escala de grises
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Aplicar umbral adaptativo para mejorar el contraste
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    
    return thresh

def divide_into_grid(image, rows=5, cols=5):
    height, width = image.shape
    cell_height = height // rows
    cell_width = width // cols
    
    grid_cells = []
    for i in range(rows):
        for j in range(cols):
            x_start = j * cell_width
            y_start = i * cell_height
            cell = image[y_start:y_start + cell_height, x_start:x_start + cell_width]
            grid_cells.append(cell)
    
    return grid_cells

def save_cells(cells):
    for idx, cell in enumerate(cells):
        cv2.imwrite(f"cell_{idx + 1}.png", cell)  # Guardar cada celda como imagen

def preprocess_and_divide(image_path):
    preprocessed_image = preprocess_image(image_path)
    grid_cells = divide_into_grid(preprocessed_image)
    save_cells(grid_cells)
    return grid_cells