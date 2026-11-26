# This is the main script file

# convert the image file in the folder to a low resolution 2D array of 1s and 0s

import os
from PIL import Image

pitch_um = 180
max_num_balls_1_dim = 120
length_long_edge_mm = max_num_balls_1_dim * pitch_um / 1000

# origin of the ball placing pattern in mm in the absolute coordinate system of the ball placer machine
# this corresponds to the bottom left pixel of the image
origin = (137.0, 148.0)

# load the image file in the same folder as this script
script_folder = os.path.dirname(os.path.abspath(__file__))
image_extensions = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tif", ".tiff", ".webp")

image_path = os.path.join(script_folder, "silab_logo.png")

if image_path is None:
	raise FileNotFoundError(f"No image file found in {script_folder}")

# open image file
image = Image.open(image_path)

# scale the image to a maximum dimension of 200 pixels while maintaining the aspect ratio
scale = max_num_balls_1_dim / max(image.size)
image = image.resize(
	(max(1, round(image.width * scale)), max(1, round(image.height * scale))),
	Image.Resampling.LANCZOS,
)
image.save(os.path.join(script_folder, f"image_scaled_to_{max_num_balls_1_dim}.png"), format="PNG")

# convert the image to pure black and white
image = image.convert("RGB")
image.putdata(
    [(255, 255, 255) if all(channel >= 180 for channel in pixel) else (0, 0, 0) for pixel in image.get_flattened_data()]
)
image.save(os.path.join(script_folder, f"bw_image_scaled_to_{max_num_balls_1_dim}.png"), format="PNG")

# print the image to the console as a grid of * and spaces
pixels = list(image.get_flattened_data())
for y in range(image.height):
	print("".join(" " if pixel == (255, 255, 255) else "*" for pixel in pixels[y * image.width:(y + 1) * image.width]))

# print the number of black pixels in the converted image
num_balls = sum(1 for pixel in pixels if pixel == (0, 0, 0))
print(f"Number of solder balls in the final image: {num_balls}")
print(f"Length of long edge: {length_long_edge_mm:.2f}mm")

# go through the pixels from bottom left up every column and print the coordinates of the black pixels in mm in the absolute coordinate system of the ball placer machine
ball_number = 1
print("Coordinates of solder balls in mm:")
coordinates_path = os.path.join(script_folder, f"ball_coordinates_width_{length_long_edge_mm}_mm_{max_num_balls_1_dim}_balls_{num_balls}_total_balls.txt")
with open(coordinates_path, "w", encoding="utf-8") as coordinates_file:
    for x in range(image.width):
        for y in range(image.height):
            pixel = pixels[(image.height - 1 - y) * image.width + x]
            if pixel == (0, 0, 0):
                x_mm = origin[0] + x * pitch_um / 1000
                y_mm = origin[1] + y * pitch_um / 1000
                coordinate = f"P{ball_number:04d}        {x_mm:.3f}     {y_mm:.3f}     000.000     0"
                print(coordinate)
                coordinates_file.write(coordinate + "\n")
                ball_number += 1
