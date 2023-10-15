for f in ./*.py;
do
  if ! [[ $f =~ "/code.py" ]];
    then
    mpy-cross $f;
  fi;
done;

cp -r lib *.mpy code.py /Volumes/CIRCUITPY/
