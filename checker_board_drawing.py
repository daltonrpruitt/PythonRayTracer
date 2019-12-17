import numpy as np
from PIL import Image
import math
import datetime

# timing_testing.testing_ray_timing()
height, width = 512, 512
image_data = np.zeros(shape=(height, width, 3), dtype=np.uint8)
for i in range(height):
    for j in range(width):
        if math.sin(i / 20) * math.sin(j / 20) > 0:
            image_data[i, j] = [0, 0, 0]
        else:
            image_data[i, j] = [255, 255, 255]
image = Image.fromarray(image_data, "RGB")
image.show()
image.save(f"Testing Image Creation - CheckerBoard - {datetime.datetime.now().strftime('%d-%m-%y__%H-%M-%S')}.png")
