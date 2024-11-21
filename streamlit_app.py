import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

st.title("Tableau de bord des utilisateurs")

# Connexion à la base de données
conn = psycopg2.connect(
    dbname="etl",
    user="etl",
    password="etl",
    host="localhost",
    port="5433"
)

query = "SELECT * FROM users;"
df = pd.read_sql_query(query, conn, parse_dates=['registered_date'])

# Fermer la connexion
conn.close()

# Calcul des statistiques
total_users = len(df)
gender_counts = df['gender'].value_counts()
post_code_counts = df['post_code'].value_counts()
registration_counts = df['registered_date'].dt.year.value_counts()

# Affichage des statistiques
st.subheader("Statistiques générales")
st.write(f"**Nombre total d'utilisateurs :** {total_users}")

# Répartition par genre
st.subheader("Répartition par genre")
fig1 = px.pie(df, names='gender', title='Répartition par genre')
st.plotly_chart(fig1)

# Répartition par code postal
st.subheader("Répartition par code postal (Top 10)")
top_post_codes = post_code_counts.head(10)
fig2 = px.bar(x=top_post_codes.index, y=top_post_codes.values,
             labels={'x':'Code Postal', 'y':'Nombre d\'utilisateurs'},
             title='Top 10 des codes postaux')
st.plotly_chart(fig2)

# Répartition par année d'inscription
st.subheader("Répartition par année d'inscription")
fig3 = px.bar(x=registration_counts.index, y=registration_counts.values,
             labels={'x':'Année', 'y':'Nombre d\'inscriptions'},
             title='Inscriptions par année')
st.plotly_chart(fig3)

# Données détaillées
st.subheader("Données détaillées")
st.dataframe(df)
