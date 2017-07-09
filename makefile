


.PHONY: all doc clean

all: doc

doc:
	cd doc ; make html

clean:
	cd doc ; make clean