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

  def add(self, strand:NeoPixel, index:int|list[int], offset:float=0) -> int:
    index_list:list[int]
    if isinstance(index, list):
      index_list = index
    else:
      index_list = [index]
    for i in index_list:
      self._strands.append(strand)
      self._indices.append(i)
      self._offsets.append(offset)

    return len(self._strands)-1

  def addRange(self, strand:NeoPixel, count:int, *, start_index:int=0, index_stride:int=1, start_offset:float=0.0, offset_delta:float=0.0) -> None:
    for i in range(count):
      index = start_index + (index_stride*i)
      self.add(strand,index,start_offset + (offset_delta*i))

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

  def debug_dump(self)->str:
    lines:list[str] = []
    for i in range(len(self)):
      strand,index,offset = self.get(i)
      lines.append(f"{i}:: strand:{id(strand)} index:{index} offset:{offset}")
    return f"~~~\nstrand - {self.name}\n{"\n".join(lines)}"


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
      self._maxed_out = [[True for _ in group] for group in self.groups]

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
        progress_in_bounds = localProgress == clamped_progress
        already_maxed_out = self._maxed_out[group_index][i]
        if progress_in_bounds or not already_maxed_out:
          # if local_progress is between 0 and 1 OR the last update was between 0 and 1 - do an update
          #     we need the OR not already_maxed_out to allow the progress to be set once, and only once,
          #     after going below 0, or going passed 1
          group.set(i, self.getColor(clamped_progress))
          # print(self.name, group_index, i, "local-progress:", round(localProgress,4), "-", clamped_progress)
          # if clamped_progress != localProgress:
          #   print(f"------------------ {self.name} {group_index}_{i} maxed -------------------")
        self._maxed_out[group_index][i] = clamped_progress != localProgress

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
  loops_left:int = 0
  next_routine:NeoTweenRoutine|None = None # type: ignore
  prev_routine:NeoTweenRoutine|None = None # type: ignore

  # FUTURE FEATURE TODO:
  # rename this to NeoTweenSequence, and make a new NeoTweenRoutine class that handles multiple NeoTweenSequences

  __slots__ = "name","tweens","_startedAt","next_routine","prev_routine"

  def __init__(self, name:str):
    self.name = name
    self.tweens = []
    self._startedAt = None

  def start(self):
    self._startedAt = time.monotonic()
    self.update()

  def getDuration(self)->float:
    return max(tween.getDurationWithDelayAndOffsets() for tween in self.tweens)

  def updateTween(self, tween:NeoTween, delta:float)->None|NeoTweenRoutine: # type: ignore
    progress = (delta - tween.delay) / tween.duration
    tween.setProgress(progress)

  def update(self)->None|NeoTweenRoutine: # type: ignore
    now = time.monotonic()
    if self._startedAt == None:
      return None

    duration = self.getDuration()
    delta = now - self._startedAt

    # print(f"==tick==================================== {now - self._startedAt}%{duration}={delta} ")
    [self.updateTween(tween, delta) for tween in self.tweens]

    if delta > duration:
      curr_started_at = self._startedAt
      self._startedAt = None
      if self.loops_left > 0:
        self.loops_left -= 1
        self._startedAt = curr_started_at + duration
      elif self.next_routine != None:
        return self.next_routine
      elif self.prev_routine != None:
        curr_routine = self.prev_routine
        while curr_routine.prev_routine != None:
          curr_routine = curr_routine.prev_routine
        return curr_routine
      else:
        print(f"{self.name} - End of routine")


  def debug_dump(self, samples=2)->str:
    tween_strs = [tween.debug_dump(samples) for tween in self.tweens]
    return f"===========\nroutine-bldr-dump: {self.name}\nduration: {self.getDuration()}\n---------\n{"\n---------\n".join(tween_strs)}"


class NeoTweenRoutineMachine:
  groups:list[NeoPixelGroup]
  routine:NeoTweenRoutine
  relativeDelays:list[float]

  def __init__(self,*, name:str, groups:list[NeoPixelGroup], initialColor:ColorTuple=ColorTuple(0,0,0,0.0), duration:float=1.0, delay:float=0.0):
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

  def nextRoutine(self,*, name:str, groups:list[NeoPixelGroup]|None=None, initialColor:ColorTuple|None=None, duration:float=1.0, delay:float=0.0):
    if initialColor == None:
      if len(self.routine.tweens) > 0:
        initialColor = self.routine.tweens[0].toColor
      else:
        initialColor = ColorTuple(0,0,0,0.0)
    if groups == None:
      groups = self.groups
    new_factory = NeoTweenRoutineMachine(name=name,groups=groups,initialColor=initialColor,duration=duration,delay=delay)
    self.routine.next_routine = new_factory.routine
    new_factory.routine.prev_routine = self.routine
    return new_factory

  def oldest(self)->NeoTweenRoutine:
    oldest = self.routine
    while oldest.prev_routine != None:
      oldest = oldest.prev_routine
    return oldest

  def start(self)->None:
    self.routine = self.oldest()
    self.routine.start()
    last_change = time.monotonic()
    while True:
        now = time.monotonic()
        # if now - last_change > 0.25:
        if now - last_change > 0.1:
            last_change = now
            next_routine = self.routine.update()
            if next_routine != None:
              print("switching to next routine: ", next_routine.name)
              self.routine = next_routine
              next_routine.start()

