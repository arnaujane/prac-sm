import cv2
import numpy as np
import metrikz

# Leer imagen PNG (BGR por defecto en OpenCV)
source = cv2.imread("image1.png", cv2.IMREAD_COLOR)

# Comprobar que la imagen se ha cargado correctamente
if source is None:
    raise ValueError("No se pudo cargar image1.png")

# Mostrar propiedades equivalentes a PIL
height, width, channels = source.shape
print((width, height), f"{channels} channels", "PNG")

# Guardar como JPEG con calidad 1 (0–100)
cv2.imwrite("image1.jpg", source, [int(cv2.IMWRITE_JPEG_QUALITY), 1])

# Leer la imagen JPEG resultante
target = cv2.imread("image1.jpg", cv2.IMREAD_COLOR)

# Convertir a array NumPy explícitamente para comparar
source = np.asarray(source)
target = np.asarray(target)

# Calcular MSE
print(metrikz.mse(source, target))