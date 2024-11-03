import time
from collections import namedtuple
from neopixel import NeoPixel

ColorTuple = namedtuple("ColorTuple", ["r", "g", "b", "w"])

# def clamp(minVal:float, maxVal:float, value:float)->float:
def clamp(minVal:int|float, maxVal:int|float, value:int|float)->int|float:
  return max(minVal, min(value, maxVal))

def clampRGB(value:int)->int:
  return clamp(0, 255, value)

def clampW(value:float)->float:
  return clamp(0, 1, value)

def clampColor(color:ColorTuple)->ColorTuple:
  (r,g,b,w) = color
  if w > 10 or w < -9:
    print("warning: received white value more than 10x the min or max value. expected 0.0-1.0, got", w)
  return ColorTuple(clampRGB(r), clampRGB(g), clampRGB(b), clampW(w))

def addColors(a:ColorTuple, b:ColorTuple)->ColorTuple:
  return ColorTuple(a.r + b.r, a.g + b.g, a.b + b.b, a.w + b.w)

def subtractColors(a:ColorTuple, b:ColorTuple)->ColorTuple:
  return ColorTuple(a.r - b.r, a.g - b.g, a.b - b.b, a.w - b.w)

def multiplyColor(color:ColorTuple, multiplyBy:float)->ColorTuple:
  return ColorTuple(color.r * multiplyBy, color.g * multiplyBy, color.b * multiplyBy, color.w * multiplyBy)

class NeoPixelGroup:
  _strands: list[NeoPixel]
  _indices: list[int]
  name:str
  _offsets: list[float]

  __slots__ = "_strands", "_indices", "_offsets", "name"

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

  def add(self, strand:NeoPixel, index:int, offset:float=0) -> int:
    self._strands.append(strand)
    self._indices.append(index)
    self._offsets.append(offset)

    return len(self._strands)-1

  def get(self, index)->tuple[NeoPixel,int,float]:
    return (self._strands[index], self._indices[index], self._offsets[index])

  def set(self, index:int, color:ColorTuple) -> None:
    (strand,strandIndex,_) = self.get(index)
    strand[strandIndex] = color

  def getMaxOffset(self)->float:
   return max(offset for offset in self._offsets)

  def getLocalProgress(self, index:int, tweenProgress:float)->float:
    offset = self.get(index)[2]
    return tweenProgress - offset

  def fill(self, color:ColorTuple) -> None:
    for i in range(len(self)):
      strand = self._strands[i]
      index = self._indices[i]
      strand[index] = color
  
  def showAll(self)->None:
    [strand.show() for strand in self._strands]

# class ColorChannel(Flag):
#   RED=auto()
#   GREEN=auto()
#   BLUE=auto()
#   WHITE=auto()


class NeoTween:
  name:str
  groups:list[NeoPixelGroup]
  # enabledColors:ColorChannel = ColorChannel.RED | ColorChannel.BLUE | ColorChannel.GREEN | ColorChannel.WHITE
  fromColor:ColorTuple
  toColor:ColorTuple
  duration:int
  delay:int

  _maxed_out:list[list[bool]]

  __slots__ = "name", "groups", "fromColor", "toColor", "duration", "delay", "_maxed_out"

  def __init__ (
      self,
      *,
      name="anon",
      fromColor:ColorTuple,
      toColor:ColorTuple,
      duration:int,
      delay:int = 0,
      groups:list[NeoPixelGroup] = []
    ):
      self.name = name
      self.groups = groups
      self.fromColor = fromColor
      self.toColor = toColor
      self.duration = duration
      self.delay = delay
      self._maxed_out = [[False for _ in group] for group in self.groups]

  def getMaxOffset(self)->float:
    return max(group.getMaxOffset() for group in self.groups)

  def getDurationWithDelayAndOffsets(self)->float:
    return self.delay + self.duration + (self.duration * self.getMaxOffset())

  def add(self, group:NeoPixelGroup)->int:
    self.groups.append(group)
    return len(self.groups)

  def getColor(self, progress:float)->ColorTuple:
    # FUTURE-TODO - variable easing funcs
    # linear scaling: from + progress*(from-to)
    return clampColor(addColors(self.fromColor, multiplyColor(subtractColors(self.toColor, self.fromColor), progress)))

  def setProgress(self, progress:float)->None:
    for group_index,group in enumerate(self.groups):
      for i in range(len(group)):
        localProgress = group.getLocalProgress(i, progress)
        clamped_progress = clamp(0,1,localProgress)
        # clamped_progress = min(1,localProgress)
        already_maxed_out = self._maxed_out[group_index][i]
        if not already_maxed_out:
          group.set(i, self.getColor(clamped_progress))
        self._maxed_out[group_index][i] = clamped_progress != localProgress
        # future todo: if self.doWraparound and localProgress < 0: localProgress = 1 + localProgress

  def debug_dump(self, samples:int=2)->str:
    samples_str:list[str] = []
    for i in range(samples):
      progress = i/(samples-1)
      (r,g,b,a) = self.getColor(progress)
      samples_str.append(f"{round(progress*100, 1)}%: {r},{g},{b},{a}")
    return f"~~~\ntween: {self.name}, delay:{self.delay}, duration:{self.duration} reldur:{self.getDurationWithDelayAndOffsets()}\nsamples: ({"->".join(samples_str)})"

class NeoTweenRoutine:
  name:str
  tweens:list[NeoTween]
  _startedAt:float

  __slots__ = "name","tweens","_startedAt"

  def __init__(self, name:str):
    self.name = name
    self.tweens = []
    self._startedAt = None

  def start(self):
    self._startedAt = time.monotonic()
    self.update()

  def getDuration(self)->float:
    return max(tween.getDurationWithDelayAndOffsets() for tween in self.tweens)

  def updateTween(self, tween:NeoTween, delta:float)->None:
    progress = (delta - tween.delay) / tween.duration
    tween.setProgress(progress)

  def update(self)->None:
    now = time.monotonic()
    if self._startedAt == None:
      return

    duration = self.getDuration()
    delta = now - self._startedAt

    [self.updateTween(tween, delta) for tween in self.tweens]

    if delta > duration:
      self._startedAt += duration

  def debug_dump(self, samples=2)->str:
    tween_strs = [tween.debug_dump(samples) for tween in self.tweens]
    return f"===========\nroutine-bldr-dump: {self.name}\nduration: {self.getDuration()}\n---------\n{"\n---------\n".join(tween_strs)}"


class NeoTweenRoutineMachine:
  groups:list[NeoPixelGroup]
  routine:NeoTweenRoutine
  relativeDelays:list[float]

  def __init__(self,*, name:str, groups:NeoPixelGroup, initialColor:ColorTuple, duration:float=1.0, delay:float=0.0):
    self.groups = groups
    self.routine = NeoTweenRoutine(name)
    self.relativeDelays=[]
    self.add(fromColor=initialColor,toColor=initialColor,duration=duration,delay=delay)

  def getNextTweenName(self)->str:
    return str.format("{}-{}", self.routine.name, len(self.routine.tweens))

  def add(self, *, fromColor:ColorTuple, toColor:ColorTuple, duration:float, delay:float=0.0, name:str|None=None):
    if name == None:
      name = self.getNextTweenName()
    newTween = NeoTween(
      name=name,
      toColor=toColor,
      fromColor=fromColor,
      duration=duration,
      groups=self.groups
    )
    self.routine.tweens.append(newTween)
    self.relativeDelays.append(delay)
    newTween.delay = self.calculateStartElapsedTime()

  def getLastTween(self)->NeoTween:
    return self.routine.tweens[len(self.routine.tweens)-1]

  def calculateStartElapsedTime(self, index:int|None=None)->float:
    if index == None:
      index = len(self.relativeDelays)-1
    if index < 0:
      return 0.0
    delay = self.relativeDelays[index]
    if index == 0:
      return delay
    else:
      prevDuration = self.routine.tweens[index-1].duration
      result = delay + prevDuration + self.calculateStartElapsedTime(index-1)
      return result
  
  def toColor(self, r:int,g:int,b:int,w:float):
    self.getLastTween().toColor = ColorTuple(r,g,b,w)
    return self

  def forDuration(self, duration:float):
    self.getLastTween().duration = duration
    return self

  def delayedBy(self, delay:float):
    self.relativeDelays[len(self.relativeDelays)-1] = delay
    self.getLastTween().delay = self.calculateStartElapsedTime()
    return self

  def named(self, name:str):
    self.getLastTween().name = name

  def then(self, *, fromColor=None, toColor=None, duration:float|None=None, delay:float=0.0, name:str|None=None):
    current = self.getLastTween()

    if fromColor == None:
      fromColor = current.toColor
    if toColor == None:
      toColor = fromColor
    if duration == None:
      duration = current.duration
    self.add(fromColor=fromColor, toColor=toColor, duration=duration, delay=delay, name=name)
    return self

  def done(self)->NeoTweenRoutine:
    return self.routine

