import matlab.engine
eng = matlab.engine.start_matlab()

f = 2
eng.triarea(f)