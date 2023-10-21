# https://github.com/adafruit/Adafruit-QT-Py-PCB/blob/master/Adafruit%20QT%20Py%20SAMD21%20pinout.pdf
import time
import board
import neopixel
from Neotweens import ColorTuple, NeoPixelGroup, NeoTween, NeoTweenRoutine, NeoTweenRoutineMachine

board_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
board_pixel.brightness = 0.08

strand1 = neopixel.NeoPixel(board.A0, 8, pixel_order="GRBW")
strand1.brightness = 0.08

# groupA = NeoPixelGroup("grpA")
# groupA.add(board_pixel, 0)
# groupA.add(strand1, 0)
groupB = NeoPixelGroup("grpB")
# groupB.add(strand1, 0, 0.00)
offset=0.2
for i in range(8):
  groupB.add(strand1, i, (i*offset)%1)

# tweenA = NeoTween(
#   name="tweenA",
#   fromColor=ColorTuple(100, 100, 255, 0),
#   toColor=ColorTuple(255, 0, 0, 0),
#   duration=1.5
# )
# tweenA.add(groupA)
# tweenB = NeoTween(
#   name="tweenB",
#   fromColor=ColorTuple(100, 100, 255, 0),
#   toColor=ColorTuple(0, 255, 0, 0.0),
#   duration=0.5,
#   delay=4
# )
# tweenB.add(groupB)
# tweenB2 = NeoTween(
#   name="tweenB2",
#   fromColor=ColorTuple(0, 255, 0, 0.0),
#   toColor=ColorTuple(0, 255, 0, 0.0),
#   duration=2,
#   delay=0.5
# )
# tweenB2.add(groupB)
# tweenC = NeoTween(
#   name="tweenC",
#   fromColor=ColorTuple(0, 255, 0, 0.0),
#   toColor=ColorTuple(100, 100, 255, 0),
#   duration=0.5,
#   delay=8.5
# )
# tweenC.add(groupB)
# tweenC2 = NeoTween(
#   name="tweenC2",
#   fromColor=ColorTuple(100, 100, 255, 0),
#   toColor=ColorTuple(100, 100, 255, 0),
#   duration=1,
#   delay=5
# )
# tweenC2.add(groupB)

# routine1 = NeoTweenRoutine("routine1")
# routine1.tweens.append(tweenA)
# routine1.tweens.append(tweenB)
# routine1.tweens.append(tweenB2)
# routine1.tweens.append(tweenC)
# routine1.tweens.append(tweenC2)
# routine1.start()

m1 = NeoTweenRoutineMachine(
   name="routine1",
   groups=[groupB],
   initialColor=ColorTuple(0, 0, 255, 0)
)
m1.delayedBy(1)
m1.forDuration(0.25)
m1.toColor(100,0,0,0.5)

m1.then(name="toYellow")
m1.delayedBy(1)
m1.toColor(50,50,0,0.0)

m1.then(name="toGreen")
m1.delayedBy(1)
m1.toColor(0,100,0,0.0)

m1.then(name="toCyan")
m1.delayedBy(1)
m1.toColor(0,100,100,0.5)

m1.then(name="toBlue")
m1.toColor(0,0,100,0.5)
m1.toColor(0,0,255,0)
m1.delayedBy(1)
routine1 = m1.done()

last_change = time.monotonic()
routine1.start()

while True:
    now = time.monotonic()
    if now - last_change > 0.02:
    # if now - last_change > 0.1:
        last_change = now
        routine1.update() # TODO - simply test this




