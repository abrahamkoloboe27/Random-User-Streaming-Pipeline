from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, concat, lit, monotonically_increasing_id
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DateType, TimestampType

# Créer une session Spark
spark = SparkSession.builder \
    .appName("KafkaSparkIntegration") \
    .getOrCreate()

# Définir le schéma des données
schema = StructType([
    StructField("gender", StringType(), True),
    StructField("name", StructType([
        StructField("first", StringType(), True),
        StructField("last", StringType(), True)
    ]), True),
    StructField("dob", StructType([
        StructField("date", StringType(), True),
        StructField("age", IntegerType(), True)
    ]), True),
    StructField("location", StructType([
        StructField("city", StringType(), True),
        StructField("country", StringType(), True)
    ]), True),
    StructField("email", StringType(), True),
    StructField("phone", StringType(), True),
    StructField("registered", StructType([
        StructField("date", StringType(), True)
    ]), True)
])

# Lire les données depuis Kafka
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", 'broker-etl:29092') \
    .option("subscribe", "user_topic") \
    .load()

df = df.selectExpr("CAST(value AS STRING)")

# Parser les données JSON
user_df = df.select(from_json(col("value"), schema).alias("data")).select("data.*")

# Aplatir les champs imbriqués et ajouter les colonnes manquantes
user_df = user_df.select(
    monotonically_increasing_id().alias("id"),
    col("name.first").alias("first_name"),
    col("name.last").alias("last_name"),
    col("gender"),
    concat(col("location.city"), lit(", "), col("location.country")).alias("address"),
    lit(None).cast(StringType()).alias("post_code"),
    col("email"),
    concat(col("name.first"), lit("."), col("name.last")).alias("username"),
    col("registered.date").cast(TimestampType()).alias("registered_date"),
    col("phone"),
    lit(None).cast(StringType()).alias("picture")
)

# Écrire les données dans PostgreSQL
def write_to_postgres(batch_df, batch_id):
    batch_df.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://postgres:5433/etl") \
        .option("dbtable", "users") \
        .option("user", "etl") \
        .option("password", "etl") \
        .mode("append") \
        .save()

query = user_df.writeStream \
    .foreachBatch(write_to_postgres) \
    .start()

query.awaitTermination()
