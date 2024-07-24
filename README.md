Python requirements
- python 3.10.x+
- pip

Pre-run
1) pip install -r requirements.txt

- I have inlcuded both the in-memory code and persistent code, because in-memory was not working on Windows machine. It works fine on unix-based systems

How to run?
1) python inMemory/api.py (or) python persistent/api.py (Depending on your system, use python or python3 command)
2) Send the below POST request from Postman or through a curl command <br/>
http://localhost:8000/api/forex-data?from=GBP&to=INR&period=1M <br/>
You will be able to see the data according to the query parameters
<br/>
- I also tried to seperate the constants used in a constants file, API code in the api.py file and lastly the scraper and database functions in scrapper.py file
