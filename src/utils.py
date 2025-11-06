import cv2

def save_image(image, filename):
    """Saves an image to the specified filename."""
    cv2.imwrite(filename, image)

def load_image(filepath):
    """Loads an image from the specified filepath."""
    return cv2.imread(filepath)

def convert_to_grayscale(image):
    """Converts an image to grayscale."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def threshold_image(image, thresh_value=150):
    """Applies a binary threshold to the image."""
    _, thresh = cv2.threshold(image, thresh_value, 255, cv2.THRESH_BINARY_INV)
    return thresh

def get_cell_coordinates(cells):
    """Extracts the coordinates of the cells from the contours."""
    return [(x, y, w, h) for x, y, w, h in cells]

def sort_cells(cells):
    """Sorts the cells based on their coordinates."""
    return sorted(cells, key=lambda b: (b[1], b[0]))