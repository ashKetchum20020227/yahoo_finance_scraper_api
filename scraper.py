import requests 
from bs4 import BeautifulSoup 
import sqlite3
import datetime
import calendar
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


month_str_to_int_dict = {
    'Jan': 1,
    'Feb': 2,
    'Mar': 3,
    'Apr': 4,
    'May': 5,
    'Jun': 6,
    'Jul': 7,
    'Aug': 8,
    'Sep': 9,
    'Oct': 10,
    'Nov': 11,
    'Dec': 12
}

seconds_in_day = 60*60*24

headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"} 

conn = sqlite3.connect('file::memory:?cache=shared')
cursor = conn.cursor()

# run once per day per exchange at midnight
def scrape_new_data(from_cur, to_cur):

    conn = sqlite3.connect('file::memory:?cache=shared')
    cursor = conn.cursor()

    cur_time = datetime.datetime.now()
    cur_time = cur_time - datetime.timedelta(days=1)
    cur_time_epoch = calendar.timegm(cur_time.timetuple())

    soup = get_html(from_cur, to_cur, cur_time_epoch, cur_time_epoch)

    exchange_rate_table_body = soup.find("table", attrs={"class": "table yf-ewueuo"}).find("tbody")

    row = exchange_rate_table_body.findAll("tr")[0]
    arr = [from_cur, to_cur]
    cols = row.findAll("td")
    arr.append(cols[0].contents[0])
    for j in range(1, len(cols) - 1):
        arr.append(float(cols[j].contents[0]))
        
    arr[2] = convert_date_string_to_date(arr[2])

    query = """INSERT INTO FOREX_DATA VALUES (?,?,?,?,?,?,?,?)"""
    cursor.execute(query, arr)
    conn.commit()


def convert_date_string_to_date(date):
    month = month_str_to_int_dict[date.split(", ")[0].split(" ")[0]]
    day = int(date.split(", ")[0].split(" ")[1])
    year = int(date.split(", ")[1].strip())
    new_date = datetime.datetime(year, month, day, 0, 0)
    return new_date


def get_html(from_cur, to_cur, from_epoch, to_epoch):
    URL = "https://finance.yahoo.com/quote/" + from_cur + to_cur + "=X/history/?period1=" + str(from_epoch) + "&period2=" + str(to_epoch)
    r = requests.get(URL, headers=headers)
    soup = BeautifulSoup(r.content, 'html5lib')
    return soup


# days = number of days to be subtracted from today
def scrape_historical_data(from_cur, to_cur, from_epoch, to_epoch):

    soup = get_html(from_cur, to_cur, from_epoch, to_epoch)

    exchange_rate_table_body = soup.find("table", attrs={"class": "table yf-ewueuo"}).find("tbody")

    for row in exchange_rate_table_body.findAll("tr"):
        arr = [from_cur, to_cur]
        cols = row.findAll("td")
        arr.append(cols[0].contents[0])
        for j in range(1, len(cols) - 1):
            arr.append(float(cols[j].contents[0]))
        
        arr[2] = convert_date_string_to_date(arr[2])

        query = """INSERT INTO FOREX_DATA VALUES (?,?,?,?,?,?,?,?)"""
        cursor.execute(query, arr)
        conn.commit()


def scrape_historical_initial():
    end_time = datetime.datetime.now()
    end_time = end_time - datetime.timedelta(days=1)
    start_time = end_time - datetime.timedelta(days=366)

    end_time_epoch = calendar.timegm(end_time.timetuple())
    start_time_epoch = calendar.timegm(start_time.timetuple())

    scrape_historical_data("GBP", "INR", start_time_epoch, end_time_epoch)
    scrape_historical_data("AED", "INR", start_time_epoch, end_time_epoch)

    
def create_table():
    query = """ CREATE TABLE FOREX_DATA (
            from_cur TEXT,
            to_cur TEXT,
            entry_date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            adj_close REAL
        ); """
    
    cursor.execute(query)
    conn.commit()


def init_scheduler():
    trigger1 = CronTrigger(
        year="*", month="*", day="*", hour="0", minute="0", second="0"
    )
    trigger2 = CronTrigger(
        year="*", month="*", day="*", hour="0", minute="5", second="0"
    )
    scheduler = BackgroundScheduler({'apscheduler.job_defaults.max_instances': 2})
    scheduler.add_job(func=scrape_new_data, args=["GBP", "INR"], trigger=trigger1)
    scheduler.add_job(func=scrape_new_data, args=["AED", "INR"], trigger=trigger2)
    scheduler.start()


def main():
    create_table()
    scrape_historical_initial()
    init_scheduler()
    

# if __name__ == "__main__":
#     main()
#     while (True):
#         continue