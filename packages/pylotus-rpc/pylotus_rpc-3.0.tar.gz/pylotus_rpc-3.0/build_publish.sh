#!/bin/bash
# something like this to build and publish to pypi

source bin/activate
rm dist/*
python -m build
python -m twine upload dist/*
