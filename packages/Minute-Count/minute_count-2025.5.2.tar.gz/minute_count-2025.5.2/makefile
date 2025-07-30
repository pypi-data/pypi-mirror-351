py=.venv/bin/python

build:
	make clean
	make version
	$(py) -m build

version:
	vinc

clean:
	touch dist/fuck
	rm dist/*

upload:
	make build
	$(py) -m twine upload --repository pypi dist/* $(flags)

reload:
	make upload
	pipx upgrade minute-count
	pipx upgrade minute-count
	minute-count --version .
