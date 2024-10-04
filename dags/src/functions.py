
import requests 
import uuid 
import json
from kafka import KafkaProducer
import time
import logging
import os
import psycopg2

def get_data():
    response = requests.get('https://randomuser.me/api/')
    data = response.json()
    
    logging.info(f"Data fetched")
    return data['results'][0]

def format_data(res):
    data = {}
    location = res['location']
    data['id'] = res["info"]["seed"]
    data['first_name'] = res['name']['first']
    data['last_name'] = res['name']['last']
    data['gender'] = res['gender']
    data['address'] = f"{str(location['street']['number'])} {location['street']['name']}, " \
                      f"{location['city']}, {location['state']}, {location['country']}"
    data['post_code'] = location['postcode']
    data['email'] = res['email']
    data['username'] = res['login']['username']
    data['dob'] = res['dob']['date']
    data['registered_date'] = res['registered']['date']
    data['phone'] = res['phone']
    data['picture'] = res['picture']['medium']
    logging.info(f"Data formatted")
    return data

def custom_serializer(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def stream_data():

    data = []
    producer = KafkaProducer(bootstrap_servers=['broker:29092'], max_block_ms=5000)
    curr_time = time.time()

    while True:
        if time.time() > curr_time + 10: #1 minute
            logging.info(f"Time limit reached")
            file_path = "dump/data.json"
            with open(file_path, 'w') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            break
        try:
            res = get_data()
            res = format_data(res)
            
            
            producer.send('users_created', json.dumps(res).encode('utf-8'))
            data.append(res)
        except Exception as e:
            logging.error(f'An error occured: {e}')
            continue
        
        
        
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
        CREATE TABLE IF NOT EXISTS public."users" (
            id PRIMARY KEY,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            gender VARCHAR(50),
            address VARCHAR(50),
            post_code VARCHAR(50),
            email VARCHAR(50),
            username VARCHAR(50),
            registered_date VARCHAR(50),
            phone VARCHAR(50),
            picture VARCHAR(50)
        );
        ''')
    conn.commit()
    logging.info("Table created successfully")
    return "Table created successfully"

def put_data_in_postgres_database():
    
    with open("dump/data.json", 'r') as f:
        data = json.load(f)
        logging.info("Data loaded")
        
    conn, cur = connect_to_postgres()
    for df in data : 
        cur.execute('''
            INSERT INTO public."users" (id, first_name, last_name, gender, address, post_code, email, username, registered_date, phone, picture)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (df['id'], df['first_name'],
            df['last_name'], df['gender'], df['address'],
            df['post_code'], df['email'], df['username'], 
            df['registered_date'], df['phone'], df['picture']))
        print(df)
        logging.info("Data inserted into Postgres")
        
        logging.info("Data inserted into Postgres")
        conn.commit()
    return "Data inserted into Postgres"

def clean_up_files():
    for file in os.listdir("dump"):
        file_path = os.path.join("dump", file)
        if os.path.isfile(file_path):
            os.remove(file_path)