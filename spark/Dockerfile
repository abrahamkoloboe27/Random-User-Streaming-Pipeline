FROM bitnami/spark:latest

# Installer les connecteurs Kafka
# Adapter la version de Spark à celle utilisée dans l'image Bitnami.
# Par exemple, si Spark est en version 3.3.0, utilisez la ligne suivante :
ENV SPARK_VERSION=3.3.0
ENV SCALA_BINARY_VERSION=2.12
ENV KAFKA_CLIENTS_VERSION=3.3.1

USER root
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*

# Téléchargement du connecteur spark-sql-kafka et kafka-clients
RUN wget https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_${SCALA_BINARY_VERSION}/${SPARK_VERSION}/spark-sql-kafka-0-10_${SCALA_BINARY_VERSION}-${SPARK_VERSION}.jar -P /opt/bitnami/spark/jars/ && \
    wget https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/${KAFKA_CLIENTS_VERSION}/kafka-clients-${KAFKA_CLIENTS_VERSION}.jar -P /opt/bitnami/spark/jars/

USER 1001
WORKDIR /opt/bitnami/spark
