# https://github.com/adafruit/Adafruit-QT-Py-PCB/blob/master/Adafruit%20QT%20Py%20SAMD21%20pinout.pdf
import time
import board
import neopixel
from Neotweens import ColorTuple, NeoPixelGroup, NeoTween

board_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
board_pixel.brightness = 0.01

strand1 = neopixel.NeoPixel(board.A0, 4, pixel_order="GRBW")
strand1.brightness = 0.01
strand1[0] = ColorTuple(255, 0, 0, 0)
strand1[1] = ColorTuple(0, 255, 0, 0)
strand1[2] = ColorTuple(0, 0, 255, 0)
strand1[3] = ColorTuple(155, 155, 0, 0)

groupA = NeoPixelGroup()
groupA.add(board_pixel, 0)

tweenA = NeoTween(ColorTuple(255, 0, 255, 1), ColorTuple(255, 100, 100, 1))
tweenA.add(groupA)

last_change = time.monotonic()
start_time = last_change
current_prog = 1
duration = 3

while True:
    now = time.monotonic()
    current_prog = (now - start_time) / duration
    if current_prog >= 1:
        current_prog = current_prog % 1
        start_time = now
    if now - last_change > 0.1:
        last_change = now
        tweenA.setProgress(current_prog)




