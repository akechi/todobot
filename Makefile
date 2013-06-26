


test-lingrbot:
	python3.3 -m tests.lingrbot

test-todo:
	python3.3 -m tests.todo

update: setup.sh freeze.txt
	./py3.3/bin/pip install -r freeze.txt

venvpip: setup.sh
	./setup.sh

