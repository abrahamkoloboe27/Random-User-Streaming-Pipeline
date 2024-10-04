
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
data = []
def stream_data():


    producer = KafkaProducer(bootstrap_servers=['broker:29092'], max_block_ms=5000)
    curr_time = time.time()

    while True:
        if time.time() > curr_time + 10: #1 minute
            logging.info(f"Time limit reached")
            break
        try:
            res = get_data()
            res = format_data(res)
            
            
            producer.send('users_created', json.dumps(res).encode('utf-8'))
            data.append(res)
        except Exception as e:
            logging.error(f'An error occured: {e}')
            continue
        
        file_path = "dump/data.json"
        with open(file_path, 'w') as f:
            json.dump(data, f)
        
    return "Data streamed"
        

def connect_to_postgres():
    USER = 'etl'
    PWD = 'etl'
    HOST = 'host.docker.internal'
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
    
    cur = conn.cursor()
    
    return conn, cur
   
def cretae_table():
    conn, cur = connect_to_postgres()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            gender TEXT,
            address TEXT,
            post_code TEXT,
            email TEXT,
            username TEXT,
            registered_date TEXT,
            phone TEXT,
            picture TEXT
        );
    ''')
    conn.commit()
    logging.info("Table created successfully")
    return "Table created successfully"

def put_data_in_postgres_database():
    
    with open("dump/data.json", 'r') as f:
        data = json.load(f)
    conn, cur = connect_to_postgres()
    for df in data : 
        cur.execute('''
            INSERT INTO users (id, first_name, last_name, gender, address, post_code, email, username, registered_date, phone, picture)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (df['id'], df['first_name'],
            df['last_name'], df['gender'], df['address'],
            df['post_code'], df['email'], df['username'], 
            df['registered_date'], df['phone'], df['picture']))
        logging.info("Data inserted into Postgres")
        
        logging.info("Data inserted into Postgres")
        conn.commit()
    return "Data inserted into Postgres"