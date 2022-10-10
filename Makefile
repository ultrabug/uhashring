qa:
	hatch run style:check

build:
	hatch build

clean:
	hatch clean

release: clean qa test
	hatch publish -a

test:
	hatch run +py=py310 test:test
