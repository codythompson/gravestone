# https://github.com/adafruit/Adafruit-QT-Py-PCB/blob/master/Adafruit%20QT%20Py%20SAMD21%20pinout.pdf
import time
import board
import neopixel
from Neotweens import ColorTuple, NeoPixelGroup, NeoTweenRoutineMachine

board_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
board_pixel.brightness = 0.08

strand1Len = 26
strand1 = neopixel.NeoPixel(board.A0, strand1Len, pixel_order="GRBW")
strand1.brightness = 1

strand2Len = 41
strand2 = neopixel.NeoPixel(board.A1, strand2Len)
strand2.brightness = 0.5

hangsLen = 13
hereLen = 13
hangsGroup = NeoPixelGroup("hangs")
offset=0.2
for i in range(hangsLen):
  hangsGroup.add(strand1, i, (hangsLen-i-1)*offset)
hereGroup = NeoPixelGroup("here")
for i in range(hereLen):
  hereGroup.add(strand1, i+hangsLen, ((hangsLen-1)*offset) + i*offset)
nooseGroup = NeoPixelGroup("noose")
offset=0.1
for i in range(strand2Len/2):
  nooseGroup.add(strand2, i, i*offset)
  nooseGroup.add(strand2, strand2Len-1-i, i*offset)

m1 = NeoTweenRoutineMachine(
   name="routine1",
  #  groups=[hangsGroup, hereGroup,nooseGroup],
   groups=[hangsGroup],
   initialColor=ColorTuple(0, 0, 0, 0)
)
# m1.delayedBy(1)
# m1.forDuration(0.25)
# m1.toColor(100,0,0,0.5)

# m1.then(name="toYellow")
# m1.delayedBy(1)
# m1.toColor(50,50,0,0.0)

# m1.then(name="toGreen")
# m1.delayedBy(1)
# m1.toColor(0,100,0,0.0)

# m1.then(name="toBlack")
# m1.delayedBy(0.5)
# m1.toColor(0,0,0,0.0)

# m1.then(name="toCyan")
# m1.delayedBy(2)
# m1.toColor(0,100,100,0.5)

# m1.then(name="toBlue")
# m1.toColor(0,0,100,1.0)
# m1.delayedBy(1)

# m1.then(name="toOff0")
# m1.toColor(0,0,0,1.0)
# m1.delayedBy(1)

# m1.then(name="toOff")
# m1.toColor(0,0,0,0.0)
# m1.delayedBy(1)

# m1.then(name="toOff2")
# m1.toColor(0,0,0,0.1)
# m1.delayedBy(10)
# routine1 = m1.done()

m1.toColor(0, 0, 255, 0.5)
m1.forDuration(1)
m1.delayedBy(2)

m1.then()
m1.toColor(255, 255, 255, 0.0)
m1.delayedBy(2)

m1.then()
m1.forDuration(2)
m1.toColor(0, 0, 0, 0.0)

routine1 = m1.done()
print(routine1.debug_dump(4))

last_change = time.monotonic()
routine1.start()

while True:
    now = time.monotonic()
    if now - last_change > 0.02:
    # if now - last_change > 0.1:
        last_change = now
        routine1.update() # TODO - simply test this




