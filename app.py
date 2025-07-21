import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from branca.colormap import linear
from streamlit_folium import st_folium

# Titre
st.title("🗺️ Data Viz Carte - Alsace")

# Upload de fichier de données utilisateur
uploaded_file = st.file_uploader("Charge ton fichier CSV/XLSX (avec noms de communes ou codes INSEE)", type=["csv", "xlsx"])

# Choix du nombre de classes
n_classes = st.slider("Nombre de niveaux de couleur (intensité)", min_value=2, max_value=15, value=10)

# Choix de la palette de couleurs
palette = st.selectbox("Palette de couleurs", [
    "YlOrRd", "YlGnBu", "OrRd", "PuBuGn", "BuPu", "Greens", "Blues", "Reds", "Purples"
])

# Charger le fond de carte GeoJSON de l'Alsace
@st.cache_data
def load_geojson_alsace():
    url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/regions/alsace/departements-alsace.geojson"
    return gpd.read_file(url)

geo_df = load_geojson_alsace()

if uploaded_file:
    # Lire la data
    ext = uploaded_file.name.split(".")[-1]
    df = pd.read_csv(uploaded_file) if ext == "csv" else pd.read_excel(uploaded_file)

    st.write("Aperçu de tes données :")
    st.dataframe(df.head())

    # Sélection des colonnes à mapper
    merge_key = st.selectbox("Colonne utilisée pour relier aux communes (code INSEE ou nom)", df.columns)
    value_col = st.selectbox("Colonne à visualiser (valeurs numériques)", df.select_dtypes(include='number').columns)

    # Fusion avec le fond de carte
    geo_df["code_insee"] = geo_df["code"].astype(str)
    df[merge_key] = df[merge_key].astype(str)
    merged = geo_df.merge(df, left_on="code_insee", right_on=merge_key)

    # Création de la carte
    m = folium.Map(location=[48.5, 7.5], zoom_start=8, tiles="cartodbpositron")

    # Création de la palette
    colormap = linear.__getattribute__(palette).scale(merged[value_col].min(), merged[value_col].max())
    colormap = colormap.to_step(n=n_classes)

    # Ajout des zones sur la carte
    folium.GeoJson(
        merged,
        style_function=lambda feature: {
            "fillColor": colormap(feature["properties"][value_col]),
            "color": "black",
            "weight": 0.5,
            "dashArray": "5, 5",
            "fillOpacity": 0.7,
        },
        tooltip=folium.GeoJsonTooltip(fields=[value_col, "nom"], aliases=["Valeur", "Commune"]),
    ).add_to(m)

    colormap.caption = f"Légende : {value_col}"
    colormap.add_to(m)

    # Afficher la carte dans Streamlit
    st_folium(m, width=800, height=600)

else:
    st.info("💡 Charge un fichier de données pour commencer.")
