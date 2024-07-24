Python requirements
- python 3.10.12
- pip

Pre-run
1) pip install -r requirements.txt

How to run?
1) python api.py (or) python3 api.py
2) Send the below POST request from Postman or through a curl command
http://localhost:8000/api/forex-data?from=GBP&to=INR&period=1M
You will be able to see the data according to the query parameters