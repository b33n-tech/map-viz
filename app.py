import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from branca.colormap import linear
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("🎨 Carte interactive - Communes du Bas-Rhin et Haut-Rhin (Alsace)")

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

communes = gdf[['nom', 'code']].sort_values('nom')
selected_communes = st.multiselect("🧭 Choisis les communes à colorier :", communes['nom'])

custom_values = {}
for name in selected_communes:
    code = communes[communes['nom'] == name]['code'].values[0]
    value = st.slider(f"🎛️ Intensité pour {name}", 0, 100, 50)
    custom_values[code] = value

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

gdf['valeur'] = gdf['code'].map(custom_values).fillna(0)

m = folium.Map(location=[48.5, 7.5], zoom_start=9, tiles="cartodbpositron")

colormap = palette_dict[palette].scale(gdf['valeur'].min(), gdf['valeur'].max()).to_step(n=n_classes)

folium.GeoJson(
    gdf,
    style_function=lambda feature: {
        "fillColor": colormap(feature["properties"]["valeur"]),
        "color": "black",
        "weight": 0.5,
        "fillOpacity": 0.7,
    },
    tooltip=folium.GeoJsonTooltip(fields=["nom", "valeur"], aliases=["Commune", "Valeur choisie"]),
).add_to(m)

colormap.caption = "Valeurs choisies"
colormap.add_to(m)

st_folium(m, width=1000, height=700)
