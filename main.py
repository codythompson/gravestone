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
hangsGroup.addRange(
  strand1,
  hangsLen,
  start_index=hangsLen-1,
  index_stride=-1,
  offset_delta=offset
)
hereGroup = NeoPixelGroup("here")
hereGroup.addRange(
    strand1,
    hereLen,
    start_index=hangsLen,
    start_offset=offset*hangsLen,
    offset_delta=offset
)
nooseGroup = NeoPixelGroup("noose")
offset=0.1
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

all_down_group = NeoPixelGroup("all_down")
# HERE
all_down_group.add(strand1, [13,16,19,22], 0.55)
all_down_group.add(strand1, [14,17,20,23], 0.75)
all_down_group.add(strand1, [15,18,21,24], 0.95)
# HANGS
all_down_group.add(strand1, [2,3,7,9], 0.0)
all_down_group.add(strand1, [1,4,8,11], 0.2)
all_down_group.add(strand1, [0,5,6,10,12], 0.4)
# <noose>
noose_start_offset = 0.3
noose_end_offset = 0.7
noose_offset_delta = (noose_end_offset-noose_start_offset)/strand2Half
all_down_group.addRange(
    strand2,
    int(strand2Half/2)+2, # skipping every other to avoid overloading the update loop
    index_stride=2,
    offset_delta=noose_offset_delta,
    start_offset=noose_start_offset
)
all_down_group.addRange(
    strand2,
    int(strand2Half/2),
    start_index=strand2Len-1, # skipping every other to avoid overloading the update loop
    index_stride=-2,
    offset_delta=noose_offset_delta,
    start_offset=noose_start_offset
)
# print(all_down_group.debug_dump())

# m1 = NeoTweenRoutineMachine(
#    name="routine1",
#    groups=[hangsGroup, hereGroup,nooseGroup],
#    initialColor=ColorTuple(0, 0, 0, 0)
# )
# m1.toColor(0, 0, 255, 0.0)
# m1.named("_blue")
# m1.forDuration(1)
# m1.delayedBy(2)

# m1.then(name="white")
# m1.toColor(255, 255, 255, 0.0)
# m1.delayedBy(2)

# m1.then(name="__red")
# m1.toColor(255, 0, 0, 0.0)
# m1.delayedBy(2)

# m1.then(name="green")
# m1.toColor(0, 0, 255, 0.0)
# m1.delayedBy(2)

# m1.then(name="alpha")
# m1.toColor(0, 0, 0, 1.0)
# m1.delayedBy(2)

# m1.then(name=" off")
# m1.forDuration(2)
# m1.toColor(0, 0, 0, 0.0)

# routine1 = m1.done()
# print(routine1.debug_dump(4))

lightening = NeoTweenRoutineMachine( name="lightening", groups=[all_down_group])

lightening.toColor(200,200,255,0.0)
lightening.forDuration(0.1)
# lightening.forDuration(3)
lightening.delayedBy(3)

lightening.then()
lightening.delayedBy(0.2)
lightening.forDuration(0.4)
lightening.toColor(0,0,0,0.0)

brightest_duration = 0.4
lightening.then(name="lightening brightest")
lightening.toColor(255,255,200,1.0)
lightening.forDuration(brightest_duration)
lightening.delayedBy(2)

# adding competing tweens during this time interval for a flickering effect
lightening.add(
    name="lightening flicker",
    fromColor=ColorTuple(255,255,200,1.0),
    toColor=ColorTuple(100,100,255,0.75),
    duration=brightest_duration - 0.11,
    delay= 0.09 - brightest_duration
)

lightening.then()
lightening.delayedBy(0.3)
lightening.forDuration(0.15)
lightening.toColor(0,0,0,0.0)

lightening.then()
lightening.toColor(100,100,255,0.0)
lightening.forDuration(0.2)
lightening.delayedBy(0.1)

lightening.then()
lightening.forDuration(0.25)
lightening.toColor(0,0,0,0.0)
lightening.delayedBy(0.25)

# clear it out just in case / hackfix
lightening.then()
lightening.forDuration(2)
lightening.toColor(0,0,0,0.0)

sparkle:NeoTweenRoutineMachine = lightening.nextRoutine(name="sparkle", groups=[nooseGroup])
sparkle.toColor(100,0,50,0.0)
sparkle.forDuration(1)

sparkle.then()
sparkle.toColor(0,50,100,0.25)
sparkle.forDuration(2)
# sparkle.delayedBy(-1.9)

sparkle.then()
sparkle.toColor(0,0,0,0)
sparkle.delayedBy(2)

# unofficial way to loop back to beginning
sparkle.routine.next_routine = lightening.routine

sparkle.start()





