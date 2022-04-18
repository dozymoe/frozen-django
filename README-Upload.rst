pip install --upgrade pip build
python -m build
python -m twine upload --repository testpypi dist/*
python -m twine upload --repository pypi dist/*
