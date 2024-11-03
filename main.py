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
strand2Half = int(strand2Len/2)
strand2 = neopixel.NeoPixel(board.A1, strand2Len, pixel_order="GRB")
strand2.brightness = 0.5

hangsLen = 13
hereLen = 13
hangsGroup = NeoPixelGroup("hangs")
offset=0.2
# for i in range(hangsLen):
#   hangsGroup.add(strand1, i, (hangsLen-i-1)*offset)
hangsGroup.addRange(
  strand1,
  hangsLen,
  start_index=hangsLen-1,
  index_stride=-1,
  offset_delta=offset
)
hereGroup = NeoPixelGroup("here")
# for i in range(hereLen):
#   hereGroup.add(strand1, i+hangsLen, ((hangsLen-1)*offset) + i*offset)
hereGroup.addRange(
    strand1,
    hereLen,
    start_index=hangsLen,
    start_offset=offset*hangsLen,
    offset_delta=offset
)
nooseGroup = NeoPixelGroup("noose")
offset=0.1
# for i in range(strand2Len/2):
#   nooseGroup.add(strand2, i, i*offset)
#   nooseGroup.add(strand2, strand2Len-1-i, i*offset)
nooseGroup.addRange(strand2, strand2Half+1, offset_delta=offset)
nooseGroup.addRange(
    strand2,
    strand2Half,
    start_index=strand2Len-1,
    index_stride=-1,
    start_offset=0.0,
    offset_delta=offset
)
# print(nooseGroup.debug_dump())

m1 = NeoTweenRoutineMachine(
   name="routine1",
   groups=[hangsGroup, hereGroup,nooseGroup],
   initialColor=ColorTuple(0, 0, 0, 0)
)
m1.toColor(0, 0, 255, 0.0)
m1.named("_blue")
m1.forDuration(1)
m1.delayedBy(2)

m1.then(name="white")
m1.toColor(255, 255, 255, 0.0)
m1.delayedBy(2)

m1.then(name="__red")
m1.toColor(255, 0, 0, 0.0)
m1.delayedBy(2)

m1.then(name="green")
m1.toColor(0, 0, 255, 0.0)
m1.delayedBy(2)

m1.then(name="alpha")
m1.toColor(0, 0, 0, 1.0)
m1.delayedBy(2)

m1.then(name=" off")
m1.forDuration(2)
m1.toColor(0, 0, 0, 0.0)

routine1 = m1.done()
# print(routine1.debug_dump(4))

last_change = time.monotonic()
routine1.start()

while True:
    now = time.monotonic()
    # if now - last_change > 0.25:
    if now - last_change > 0.1:
        last_change = now
        routine1.update()




