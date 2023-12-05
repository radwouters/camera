import board
import busio
import adafruit_ssd1306
import time
import io

from PIL import Image, ImageFilter
from picamera2 import Picamera2

WIDTH = 128
HEIGHT = 64  # Change to 64 if needed

camera = Picamera2()
camera.start()

i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3c)

# Clear display.
oled.fill(0)
oled.show()


while True:
    data = io.BytesIO()
    camera.capture_file(data, format='jpeg')
    
    resized = Image.open(data).resize((WIDTH, HEIGHT))

    black_and_white = resized.convert('L').filter(ImageFilter.SMOOTH).filter(ImageFilter.FIND_EDGES).filter(ImageFilter.EDGE_ENHANCE)


    # Display image
    oled.image(black_and_white.convert('1'))
    oled.show()
