# from enum import Flag, auto
from collections import namedtuple
from neopixel import NeoPixel

ColorTuple = namedtuple("ColorTuple", ["r", "g", "b", "w"])

# def clamp(minVal:float, maxVal:float, value:float)->float:
def clamp(minVal:int, maxVal:int, value:int)->int:
  return max(minVal, min(maxVal, value))

def clampRGB(value:int)->int:
  return clamp(0, 255, value)

# def clampW(value:float)->float:
#   # return clamp(0, 1, value)
#   return clamp(0, 1, value)

# def createClampedColor(r:int, g:int, b:int, w:float)->ColorTuple:
def createClampedColor(r:int, g:int, b:int, w:int)->ColorTuple:
  # return ColorTuple(clampRGB(r), clampRGB(g), clampRGB(b), clampW(w))
  return ColorTuple(clampRGB(r), clampRGB(g), clampRGB(b), clampRGB(w))

def addColors(a:ColorTuple, b:ColorTuple)->ColorTuple:
  return createClampedColor(a.r + b.r, a.g + b.g, a.b + b.b, a.w + b.w)

def subtractColors(a:ColorTuple, b:ColorTuple)->ColorTuple:
  return createClampedColor(a.r - b.r, a.g - b.g, a.b - b.b, a.w - b.w)

def multiplyColor(color:ColorTuple, multiplyBy:float)->ColorTuple:
  return createClampedColor(color.r * multiplyBy, color.g * multiplyBy, color.b * multiplyBy, color.w * multiplyBy)

class NeoPixelGroup:
  _strands: [NeoPixel]
  _indices: [int]
  name:str
  # TODO _offsets: [float] = []

  __slots__ = "_strands", "_indices", "add", "get", "write", "fill"

  def __init__(self, name:str):
    self.name = name
    self._strands = []
    self._indices = []

  def __iter__(self):
    for i in range(len(self._strands)):
      yield (self._strands[i], self._indices[i])

  def __len__(self):
    return len(self._strands)

  def add(self, strand:NeoPixel, index:int) -> int:
    self._strands.append(strand)
    self._indices.append(index)
    return len(self._strands)-1

  def get(self, index)->tuple[NeoPixel,int]:
    return [self._strands[index], self._indices[index]]

  def write(self, index:int, color:ColorTuple) -> None:
    (strand,strandIndex) = self[index]
    strand[strandIndex] = color

  def fill(self, color:ColorTuple) -> None:
    # print(self.name)
    for i in range(len(self)):
      strand = self._strands[i]
      index = self._indices[i]
      # print(index)
      strand[index] = color
  
  def showAll(self)->None:
      [strand.show() for [strand] in self]

# class ColorChannel(Flag):
#   RED=auto()
#   GREEN=auto()
#   BLUE=auto()
#   WHITE=auto()

class NeoTween:
  groups:[NeoPixelGroup]
  # enabledColors:ColorChannel = ColorChannel.RED | ColorChannel.BLUE | ColorChannel.GREEN | ColorChannel.WHITE
  fromColor:ColorTuple
  toColor:ColorTuple

  __slots__ = "groups", "fromColor", "toColor", "add", "getColor", "setProgress"

  def __init__ (self, fromColor:ColorTuple, toColor:ColorTuple):
    self.groups = []
    self.fromColor = fromColor
    self.toColor = toColor

  def add(self, group:NeoPixelGroup)->int:
    self.groups.append(group)
    return len(self.groups)

  def getColor(self, progress:float)->ColorTuple:
    # TODO - variable easing funcs
    # linear scaling: from + progress*(from-to)
    return addColors(self.fromColor, multiplyColor(subtractColors(self.toColor, self.fromColor), progress))

  def setProgress(self, progress:float)->None:
    newColor = self.getColor(progress)
    [group.fill(newColor) for group in self.groups]
    # [group.fill()]

class NeoTweens:
  """
  TODO - implement this 
    - need to handle the notion of intra-group pixel offsets
      - pixels later in the chain will finish the tween AFTER pixels earlier in the chain.
      - does NeoTween simply get sent progresses greater (or less than) 1?
        - I think so - each NeoTween has an offset itself, and parent sends progress values through the whole sequence. The values will be negative and greater than one.
  """
  def __init__():
    print("hmmmm")
