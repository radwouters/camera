import board
import busio
import adafruit_ssd1306
import io
import asyncio
import numpy
import RPi.GPIO as GPIO

from catprinter.cmds import cmds_print_img
from catprinter.ble import run_ble
from PIL import Image, ImageFilter
from picamera2 import Picamera2

WIDTH = 128
HEIGHT = 64  # Change to 64 if needed

PRINT_WIDTH = 384
PRINT_HEIGHT = 288

camera = Picamera2()
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3c)

printing = False


def boot():
    camera.start()
    # Clear display.
    oled.fill(0)
    oled.show()
    GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP) # 


async def loop():
    data = io.BytesIO()
    camera.capture_file(data, format='jpeg')
    filtered = Image.open(data).convert('L')#.filter(ImageFilter.SMOOTH).filter(ImageFilter.FIND_EDGES).filter(ImageFilter.EDGE_ENHANCE)

    resized = filtered.resize((WIDTH, HEIGHT))
    print_sized = filtered.resize((PRINT_WIDTH, PRINT_HEIGHT))

    oled.image(resized.convert('1'))
    oled.show()

    if GPIO.input(27) == GPIO.LOW and not printing:
        printing = True
        await print_photo(print_sized)
        printing = False


async def print_photo(image):
    data = cmds_print_img(~numpy.asarray(image))
    await run_ble(data, device='E1:09:05:19:DC:09')

# Display image
if __name__ == '__main__':
    boot()
    try:
        while True:
            asyncio.run(loop())
    except KeyboardInterrupt:
        camera.close()
