qa:
	hatch run style:check

build:
	hatch build

clean:
	hatch clean

release: clean qa test build
	hatch publish -u __token__

test:
	hatch run +py=py310 test:test
