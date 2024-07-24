from flask import Flask, jsonify, request 
from flask_restful import Resource, Api 
import sqlite3
import datetime

from constants import period_to_days_dict, db_name
from scraper import main

app = Flask(__name__)
api = Api(app)


class ForexData(Resource):
  
    def post(self): 
        from_cur = request.args.get("from")
        to_cur = request.args.get("to")
        period = request.args.get("period")
        
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(days=period_to_days_dict[period])
        
        conn = sqlite3.connect(db_name)
        # conn = sqlite3.connect('file::memory:?cache=shared')
        cursor = conn.cursor()
        query = """SELECT * FROM FOREX_DATA
                    WHERE from_cur = ? AND to_cur = ? AND datetime(entry_date) BETWEEN datetime(?) AND datetime(?)"""
        
        cursor.execute(query, [from_cur, to_cur, start_time, end_time])
        
        return jsonify({'data': cursor.fetchall()})


if __name__ == '__main__': 
    api.add_resource(ForexData, '/api/forex-data')
    main()
    app.run(port=8000, debug = True, use_reloader=False) 
    
   