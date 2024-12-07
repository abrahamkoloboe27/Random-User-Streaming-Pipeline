from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Créer une session Spark
spark = SparkSession.builder \
    .appName("KafkaSparkIntegration") \
    .getOrCreate()

# Définir le schéma des données reçues
schema = StructType([
    StructField("id", StringType(), True),
    StructField("first_name", StringType(), True),
    StructField("last_name", StringType(), True),
    StructField("gender", StringType(), True),
    StructField("address", StringType(), True),
    StructField("post_code", IntegerType(), True),
    StructField("email", StringType(), True),
    StructField("username", StringType(), True),
    StructField("dob", StringType(), True),
    StructField("registered_date", StringType(), True),
    StructField("phone", StringType(), True),
    StructField("picture", StringType(), True),
    StructField("age", IntegerType(), True)
])

# Lecture en streaming depuis Kafka
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "redpanda:9092") \
    .option("subscribe", "users_created") \
    .load()

# Convertir la valeur binaire en chaîne de caractères
df = df.selectExpr("CAST(value AS STRING)")

# Parser les données JSON selon le schéma
user_df = df.select(from_json(col("value"), schema).alias("data")).select("data.*")

# Convertir les dates en format Timestamp (optionnel, si nécessaire)
user_df = user_df \
    .withColumn("dob", to_timestamp("dob")) \
    .withColumn("registered_date", to_timestamp("registered_date"))

# Fonction d'écriture vers PostgreSQL
def write_to_postgres(batch_df, batch_id):
    batch_df.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://postgres:5433/etl") \
        .option("dbtable", "users") \
        .option("user", "etl") \
        .option("password", "etl") \
        .mode("append") \
        .save()

# Écriture en streaming vers PostgreSQL
query = user_df.writeStream \
    .foreachBatch(write_to_postgres) \
    .start()

query.awaitTermination()
