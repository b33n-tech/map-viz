import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from branca.colormap import linear
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("🎨 Carte interactive - Alsace par commune avec données Excel")

@st.cache_data
def load_communes_geojson():
    url_67 = "https://raw.githubusercontent.com/b33n-tech/map-viz/main/communes-67-bas-rhin.geojson"
    url_68 = "https://raw.githubusercontent.com/b33n-tech/map-viz/main/communes-68-haut-rhin.geojson"
    gdf_67 = gpd.read_file(url_67)
    gdf_68 = gpd.read_file(url_68)
    combined = pd.concat([gdf_67, gdf_68], ignore_index=True)
    combined['nom'] = combined['nom'].str.strip()
    combined['code'] = combined['code'].astype(str)
    return gpd.GeoDataFrame(combined)

gdf = load_communes_geojson()

uploaded_file = st.file_uploader(
    "📥 Upload un fichier Excel (.xlsx) avec colonnes 'Ville' et 'Niveau'",
    type=["xlsx"]
)

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # Vérification colonnes
    if not {'Ville', 'Niveau'}.issubset(df.columns):
        st.error("Le fichier doit contenir les colonnes 'Ville' et 'Niveau'")
        st.stop()

    # Normalisation noms villes (trim + minuscules)
    df['Ville_norm'] = df['Ville'].str.strip().str.lower()
    gdf['nom_norm'] = gdf['nom'].str.strip().str.lower()

    # On garde uniquement la colonne utile dans df
    df = df[['Ville_norm', 'Niveau']]

    # Agréger si plusieurs lignes par ville (ex: prendre max ou sum)
    df_agg = df.groupby('Ville_norm').agg({'Niveau':'max'}).reset_index()

    # Merge GeoDataFrame avec df
    merged = gdf.merge(df_agg, left_on='nom_norm', right_on='Ville_norm', how='left')

    merged['Niveau'] = merged['Niveau'].fillna(0)

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
    palette = st.selectbox("🎨 Palette de couleurs", list(palette_dict.keys()))
    n_classes = st.slider("📊 Nombre de niveaux", 2, 15, 10)

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

    colormap.caption = "Niveau"
    colormap.add_to(m)

    st_folium(m, width=1000, height=700)

else:
    st.info("⌛ Upload un fichier Excel avec colonnes 'Ville' et 'Niveau'")
