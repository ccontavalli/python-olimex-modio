default:
	@echo "Nothing to do. Just copy modio.py (or the whole directory)"
	@echo "wherever it is most convenient for you. Read the README or"
	@echo "run 'pydoc ./modio.py' for SETUP instructions."

all: test doc

test:
	python ./modio_test.py

doc:
	pydoc ./modio.py |sed -e 's@[^ \t]*/modio.py@modio.py@' > ./README
