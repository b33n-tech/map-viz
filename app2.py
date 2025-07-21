import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from branca.colormap import linear
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("🎨 Carte interactive - Alsace avec données Excel")

@st.cache_data
def load_geojsons():
    url_67 = "https://raw.githubusercontent.com/b33n-tech/map-viz/main/communes-67-bas-rhin.geojson"
    url_68 = "https://raw.githubusercontent.com/b33n-tech/map-viz/main/communes-68-haut-rhin.geojson"
    gdf_67 = gpd.read_file(url_67)
    gdf_68 = gpd.read_file(url_68)
    gdf_67['code'] = gdf_67['code'].astype(str)
    gdf_68['code'] = gdf_68['code'].astype(str)
    combined = pd.concat([gdf_67, gdf_68], ignore_index=True)
    return gpd.GeoDataFrame(combined)

gdf = load_geojsons()

uploaded_file = st.file_uploader("📥 Upload ton fichier Excel (.xlsx) avec colonnes 'Ville' et 'Niveau'", type=['xlsx'])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Erreur lecture fichier Excel : {e}")
        st.stop()

    # Vérification colonnes
    if not {'Ville', 'Niveau'}.issubset(df.columns):
        st.error("Le fichier doit contenir les colonnes 'Ville' et 'Niveau'")
        st.stop()

    df['Ville'] = df['Ville'].astype(str)
    df['Niveau'] = pd.to_numeric(df['Niveau'], errors='coerce')
    df = df.dropna(subset=['Niveau'])

    # Merge sur nom de commune (col 'nom' dans GeoDataFrame)
    merged = gdf.merge(df, left_on='nom', right_on='Ville', how='left')
    merged['Niveau'] = merged['Niveau'].fillna(0)

    # Choix palette
    palette_dict = {
        "YlOrRd": linear.YlOrRd_09,
        "YlGnBu": linear.YlGnBu_09,
        "OrRd": linear.OrRd_09,
        "PuBuGn": linear.PuBuGn_09,
        "BuPu": linear.BuPu_09,
        "Greens": linear.Greens_09,
        "Blues": linear.Blues_09,
        "Reds": linear.Reds_09,
        "Purples": linear.Purples_09
    }
    available_palettes = list(palette_dict.keys())
    palette = st.selectbox("🎨 Palette de couleurs", available_palettes)
    n_classes = st.slider("📊 Nombre de niveaux", 2, 15, 10)

    # Carte
    m = folium.Map(location=[48.5, 7.5], zoom_start=9, tiles="cartodbpositron")

    colormap = palette_dict[palette].scale(merged['Niveau'].min(), merged['Niveau'].max()).to_step(n=n_classes)

    folium.GeoJson(
        merged,
        style_function=lambda feature: {
            "fillColor": colormap(feature["properties"]["Niveau"]),
            "color": "black",
            "weight": 0.5,
            "fillOpacity": 0.7,
        },
        tooltip=folium.GeoJsonTooltip(fields=["nom", "Niveau"], aliases=["Commune", "Niveau"]),
    ).add_to(m)

    colormap.caption = "Niveau importé"
    colormap.add_to(m)

    st_folium(m, width=1000, height=700)

else:
    st.info("⌛ Upload un fichier Excel avec une colonne 'Ville' (nom des communes) et une colonne 'Niveau' (valeur numérique).")
