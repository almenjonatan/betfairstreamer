SOURCE="${BASH_SOURCE[0]}"

pip install wheel

cd `dirname $SOURCE/..`

echo `dirname $SOURCE`

isort -rc ./betfairstreamer
black ./betfairstreamer --line-length=120
python setup.py sdist bdist_wheel

cd `dirname $SOURCE`
