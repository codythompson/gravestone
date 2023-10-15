# https://github.com/adafruit/Adafruit-QT-Py-PCB/blob/master/Adafruit%20QT%20Py%20SAMD21%20pinout.pdf
import time
import board
import neopixel
from Neotweens import ColorTuple, NeoPixelGroup, NeoTween

board_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
board_pixel.brightness = 0.1

strand1 = neopixel.NeoPixel(board.A0, 4, pixel_order="GRBW")
strand1.brightness = 0.1

groupA = NeoPixelGroup("grpA")
groupA.add(board_pixel, 0)
groupB = NeoPixelGroup("grpB")
groupB.add(strand1, 0, 0.00)
groupB.add(strand1, 1, 0.05)
groupB.add(strand1, 2, 0.05)
groupB.add(strand1, 3, 0.05)

tweenA = NeoTween(
  name="tweenA",
  fromColor=ColorTuple(100, 100, 255, 0),
  toColor=ColorTuple(255, 0, 0, 0),
  duration=5
)
tweenA.add(groupA)
tweenB = NeoTween(
  name="tweenB",
  fromColor=ColorTuple(255, 0, 0, 0),
  toColor=ColorTuple(0, 255, 0, 2.1),
  duration=1
)
tweenB.add(groupB)

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
        tweenB.setProgress(current_prog)




