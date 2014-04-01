# Makefile

MD=md
DEL=del /f
COPY=copy /y
PYTHON=python

DESTDIR=%UserProfile%\bin\pyrexecd

all:

clean:
	-$(DEL) *.pyc *.pyo

install: 
	-$(MD) $(DESTDIR)
	$(COPY) PyRexec.py $(DESTDIR)\PyRexec.pyw
	$(COPY) *.ico $(DESTDIR)
