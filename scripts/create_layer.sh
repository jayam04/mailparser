rm -rf build/python
rm -rf build/python.zip

pip install -r requirements.txt --target=build/python

cd build
zip -r python.zip python/*
rm -rf python