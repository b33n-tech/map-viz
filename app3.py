import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from branca.colormap import linear
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("🎨 Carte interactive - Départements Bas-Rhin & Haut-Rhin")

@st.cache_data
def load_dept_geojsons():
    url_67 = "https://raw.githubusercontent.com/b33n-tech/map-viz/main/departement-67-bas-rhin.geojson"
    url_68 = "https://raw.githubusercontent.com/b33n-tech/map-viz/main/departement-68-haut-rhin.geojson"
    gdf_67 = gpd.read_file(url_67)
    gdf_68 = gpd.read_file(url_68)
    combined = pd.concat([gdf_67, gdf_68], ignore_index=True)
    return gpd.GeoDataFrame(combined)

gdf = load_dept_geojsons()

# Ici on suppose que dans ces fichiers, tu as un champ 'nom' pour le nom du département ou autre
# Si ce n’est pas le cas, adapte selon les propriétés disponibles dans ton GeoJSON
dept_names = gdf['nom'] if 'nom' in gdf.columns else st.write("Attention: champ 'nom' absent dans GeoJSON")

selected_depts = st.multiselect("Sélectionne le département à afficher :", options=gdf['nom'].unique() if 'nom' in gdf.columns else [])

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

# Par défaut on colorie tout à 50 (ou selon autre logique)
gdf['valeur'] = 50

if selected_depts:
    gdf_display = gdf[gdf['nom'].isin(selected_depts)]
else:
    gdf_display = gdf

m = folium.Map(location=[48.5, 7.5], zoom_start=9, tiles="cartodbpositron")

colormap = palette_dict[palette].scale(gdf_display['valeur'].min(), gdf_display['valeur'].max()).to_step(n=n_classes)

folium.GeoJson(
    gdf_display,
    style_function=lambda feature: {
        "fillColor": colormap(feature["properties"].get("valeur", 50)),
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.7,
    },
    tooltip=folium.GeoJsonTooltip(fields=["nom", "valeur"], aliases=["Département", "Valeur"]),
).add_to(m)

colormap.caption = "Valeur fixe par défaut"
colormap.add_to(m)

st_folium(m, width=1000, height=700)
