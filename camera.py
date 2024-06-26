import board
import busio
import adafruit_ssd1306
import io
import asyncio
import numpy as np
import RPi.GPIO as GPIO
import multiprocessing
import time


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
    GPIO.setup(26, GPIO.OUT)
    start_printer_process = multiprocessing.Process(target=start_printer)
    start_printer_process.start()
    camera.start()
    # Clear display.
    oled.fill(0)
    oled.show()
    GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def loop():
    data = io.BytesIO()
    camera.capture_file(data, format='jpeg')
    filtered = Image.open(data).convert('L')

    resized = filtered.resize((WIDTH, HEIGHT))
    print_sized = filtered.resize((PRINT_WIDTH, PRINT_HEIGHT))

    oled.image(resized.convert('1'))
    oled.show()

    if GPIO.input(27) == GPIO.LOW and not printing:
        print('Print process called')
        print_process = multiprocessing.Process(target=print_photo, args=[print_sized])
        print_process.start()
        print('Print process done')


def print_photo(image):
    print('Start printing')
    global printing
    printing = True
    treshold = np.array(image) > 127
    data = cmds_print_img(~treshold)
    asyncio.run(run_ble(data, device='E1:09:05:19:DC:09'))
    printing = False
    print('stop printing')

def start_printer():
    print('start printer')
    GPIO.output(26, GPIO.HIGH)
    time.sleep(2)
    GPIO.output(26, GPIO.LOW)
    print('printer on?')


# Display image
if __name__ == '__main__':
    boot()
    try:
        while True:
            loop()
    except KeyboardInterrupt:
        camera.close()
