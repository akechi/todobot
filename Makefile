


test: todo_py test_todo.py freeze.txt setup.sh
	python3.3 test_todo.py 

update: setup.sh freeze.txt
	./py3.3/bin/pip install -r freeze.txt

venvpip: setup.sh
	./setup.sh

