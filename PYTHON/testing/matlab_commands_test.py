import matlab.engine
eng = matlab.engine.start_matlab()
eng.triarea(nargout=0)