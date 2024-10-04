
import requests 
import uuid 
import json
from kafka import KafkaProducer
import time
import logging
import psycopg2

def get_data():
    response = requests.get('https://randomuser.me/api/')
    data = response.json()
    logging.info(f"Data fetched")
    return data['results'][0]

def format_data(res):
    location = res['location']
    data = {
        'id': str(uuid.uuid4()),  # Generate a unique ID
        'first_name': res['name']['first'],
        'last_name': res['name']['last'],
        'gender': res['gender'],
        'address': f"{location['street']['number']} {location['street']['name']}, " 
                   f"{location['city']}, {location['state']}, {location['country']}",
        'post_code': location['postcode'],
        'email': res['email']  
    }
    logging.info(f"Data formatted")
    return data

def stream_data():


    producer = KafkaProducer(bootstrap_servers=['broker:29092'], max_block_ms=5000)
    curr_time = time.time()

    while True:
        if time.time() > curr_time + 60: #1 minute
            logging.info(f"Time limit reached")
            break
        try:
            res = get_data()
            res = format_data(res)

            producer.send('users_created', json.dumps(res).encode('utf-8'))
        except Exception as e:
            logging.error(f'An error occured: {e}')
            continue
        

def connect_to_postgres():
    USER = 'etl'
    PWD = 'etl'
    HOST = 'confluent'
    DB = 'etl'
    PORT = '5433'
    
    conn = psycopg2.connect(
        dbname=DB,
        user=USER,
        password=PWD,
        host=HOST,
        port=PORT
    )
    logging.info(f"Connected to Postgres")
    return conn
    
    
    
def put_data_in_postgres_database():
    pass