# Makefile

DEL=del /f
COPY=copy /y
PYTHON=python

DESTDIR=%UserProfile%\bin

all:

clean:
	-$(DEL) *.pyc *.pyo

install: 
	$(COPY) PyRexec.py $(DESTDIR)\PyRexec.pyw
	$(COPY) *.ico $(DESTDIR)
