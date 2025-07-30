all:

dist:
	python -m build

install:
	pip install --force-reinstall --no-build-isolation --no-deps .

uninstall:
	PYTHONPATH= pip uninstall sply

upload:
	twine upload dist/*

clean:
	rm -rf build sply.egg-info dist

test_chat:
	PYTHONPATH="." bin/sply_chat_interact.py $(test_args)

