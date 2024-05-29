# Add dependencies
cd .venv/lib/python3.10/site-packages/
zip -r ../../../../package.zip .

# Add source code
cd ../../../../
zip -r package.zip *.py
