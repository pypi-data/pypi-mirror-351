


all: upload

upload:
	rm -rf dist
	@if [ ! -f token ]; then echo "Error: token file not found"; exit 1; fi
	uv build && uv publish --token $(shell cat token)