import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
import folium
from branca.colormap import linear
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("Carte Alsace - fond blanc et contours conditionnels")

@st.cache_data
def load_communes_geojson():
    url_67 = "https://raw.githubusercontent.com/b33n-tech/map-viz/main/communes-67-bas-rhin.geojson"
    url_68 = "https://raw.githubusercontent.com/b33n-tech/map-viz/main/communes-68-haut-rhin.geojson"
    gdf_67 = gpd.read_file(url_67)
    gdf_68 = gpd.read_file(url_68)
    combined = pd.concat([gdf_67, gdf_68], ignore_index=True)
    combined['nom'] = combined['nom'].str.strip()
    combined['code'] = combined['code'].astype(str)
    combined["geometry"] = combined["geometry"].simplify(tolerance=0.001)
    return combined

gdf = load_communes_geojson()

uploaded_file = st.file_uploader(
    "📥 Upload un fichier Excel (.xlsx) avec colonnes 'Ville' et 'Niveau'",
    type=["xlsx"]
)

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    if not {'Ville', 'Niveau'}.issubset(df.columns):
        st.error("Le fichier doit contenir les colonnes 'Ville' et 'Niveau'")
        st.stop()

    df['Ville_norm'] = df['Ville'].str.strip().str.lower()
    gdf['nom_norm'] = gdf['nom'].str.strip().str.lower()

    merged = gdf.merge(df[['Ville_norm', 'Niveau']], left_on='nom_norm', right_on='Ville_norm', how='left')
    merged['Niveau'] = merged['Niveau'].fillna(0)
    merged['Niveau_log'] = np.log1p(merged['Niveau'])

    palette_dict = {
        "YlGnBu": linear.YlGnBu_09,
        "PuBuGn": linear.PuBuGn_09,
        "Greens": linear.Greens_09,
        "Blues": linear.Blues_09,
    }
    palette = st.selectbox("🎨 Palette de couleurs", list(palette_dict.keys()))
    n_classes = st.slider("📊 Nombre de niveaux", 2, 10, 6)

    m = folium.Map(location=[48.5, 7.5], zoom_start=9, tiles=None)  # tiles=None pour fond blanc

    colormap = palette_dict[palette].scale(merged['Niveau_log'].min(), merged['Niveau_log'].max()).to_step(n=n_classes)

    def style_function(feature):
        niveau = feature["properties"]["Niveau"]
        if niveau > 0:
            color = "black"
            weight = 1
            fill_opacity = 0.8
        else:
            color = "#cccccc"
            weight = 0.3
            fill_opacity = 0.3
        return {
            "fillColor": colormap(feature["properties"]["Niveau_log"]),
            "color": color,
            "weight": weight,
            "fillOpacity": fill_opacity,
        }

    folium.GeoJson(
        merged,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=["nom", "Niveau"], aliases=["Ville", "Niveau"]),
    ).add_to(m)

    colormap.caption = "Niveau (échelle logarithmique)"
    colormap.add_to(m)

    st_folium(m, width=1000, height=700)

else:
    st.info("⌛ Upload un fichier Excel avec colonnes 'Ville' et 'Niveau'")
