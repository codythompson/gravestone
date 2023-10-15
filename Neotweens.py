# from enum import Flag, auto
from collections import namedtuple
from neopixel import NeoPixel

ColorTuple = namedtuple("ColorTuple", ["r", "g", "b", "w"])

# def clamp(minVal:float, maxVal:float, value:float)->float:
def clamp(minVal:int, maxVal:int, value:int)->int:
  return max(minVal, min(maxVal, value))

def clampRGB(value:int)->int:
  return clamp(0, 255, value)

def clampW(value:float)->float:
  return clamp(0, 1, value)

def createClampedColor(r:int, g:int, b:int, w:float)->ColorTuple:
  if (w > 2 or w < -1):
    print("warning: received white value more than 2x the min or max value. expected 0.0-1.0, got", w)
  return ColorTuple(clampRGB(r), clampRGB(g), clampRGB(b), clampW(w))

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
  _offsets: [float]

  __slots__ = "_strands", "_indices", "_offsets", "add", "get", "set", "fill", "showAll", "getLocalProgress"

  def __init__(self, name:str):
    self.name = name
    self._strands = []
    self._indices = []
    self._offsets = []

  def __iter__(self):
    for i in range(len(self._strands)):
      yield (self._strands[i], self._indices[i], self._offsets[i])

  def __len__(self):
    return len(self._strands)

  def add(self, strand:NeoPixel, index:int, offsetFromPrevious:float=0) -> int:
    previousOffset = 0
    if (len(self) > 0):
      # we store the cumulative offset so we don't have to re-calculate ever time we set the color
      previousOffset = self.get(len(self._offsets)-1)[2]
    self._strands.append(strand)
    self._indices.append(index)
    self._offsets.append(previousOffset+offsetFromPrevious)

    return len(self._strands)-1

  def get(self, index)->tuple(NeoPixel,int,float):
    return (self._strands[index], self._indices[index], self._offsets[index])

  def set(self, index:int, color:ColorTuple) -> None:
    (strand,strandIndex,unused) = self.get(index)
    strand[strandIndex] = color

  def getLocalProgress(self, index:int, tweenProgress:float)->float:
    offset = self.get(index)[2]
    return tweenProgress - offset

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
  name:str
  groups:[NeoPixelGroup]
  # enabledColors:ColorChannel = ColorChannel.RED | ColorChannel.BLUE | ColorChannel.GREEN | ColorChannel.WHITE
  fromColor:ColorTuple
  toColor:ColorTuple
  duration:int
  delay:int = 0

  __slots__ = "groups", "name", "fromColor", "toColor", "duration", "delay", "add", "getColor", "setProgress"

  def __init__ (
      self,
      *,
      name="anon",
      fromColor:ColorTuple,
      toColor:ColorTuple,
      duration:int,
      delay:int = 0
    ):
      self.name = name
      self.groups = []
      self.fromColor = fromColor
      self.toColor = toColor
      self.duration = duration
      self.delay = delay

  def add(self, group:NeoPixelGroup)->int:
    self.groups.append(group)
    return len(self.groups)

  def getColor(self, progress:float)->ColorTuple:
    # TODO - variable easing funcs
    # linear scaling: from + progress*(from-to)
    return addColors(self.fromColor, multiplyColor(subtractColors(self.toColor, self.fromColor), progress))

  def setProgress(self, progress:float)->None:
    for group in self.groups:
      for i in range(len(group)):
        localProgress = group.getLocalProgress(i, progress) % 1 # TODO - put the mod1 rolover behind a setting flag
        group.set(i, self.getColor(localProgress))
