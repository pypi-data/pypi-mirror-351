#!/bin/sh -e
rm -rf dist
rm -rf *.egg-info
python setup.py sdist
python -m twine upload dist/*
