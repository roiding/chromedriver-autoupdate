rm -rf build/ chromedriver_autoupdate.egg-info/ dist
python setup.py sdist bdist_wheel 
python -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*