import streamlit as st
import geopandas as gpd
import folium
from branca.colormap import linear
from streamlit_folium import st_folium

# ---- CONFIG ----
st.set_page_config(layout="wide")
st.title("🎨 Carte manuelle du Bas-Rhin")

# Charger les communes du 67
@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/b33n-tech/map-viz/main/communes-67-bas-rhin.geojson"
    return gpd.read_file(url)

gdf = load_geojson()
gdf['code'] = gdf['code'].astype(str)

# Interface : choisir les communes à colorer
communes = gdf[['nom', 'code']].sort_values('nom')
selected_communes = st.multiselect("Choisis les communes à colorer :", communes['nom'])

# Créer un dictionnaire {code: valeur}
custom_values = {}
for name in selected_communes:
    code = communes[communes['nom'] == name]['code'].values[0]
    value = st.slider(f"Intensité pour {name}", 0, 100, 50)
    custom_values[code] = value

# Palette
palette = st.selectbox("Palette de couleurs", ["YlOrRd", "Viridis", "Blues", "Greens", "Reds", "Purples"])
n_classes = st.slider("Nombre de niveaux", 2, 15, 10)

# Ajouter une colonne "valeur" pour la coloration
gdf['valeur'] = gdf['code'].map(custom_values).fillna(0)

# Carte
m = folium.Map(location=[48.6, 7.6], zoom_start=9, tiles="cartodbpositron")
colormap = linear.__getattribute__(palette).scale(gdf['valeur'].min(), gdf['valeur'].max())
colormap = colormap.to_step(n=n_classes)

folium.GeoJson(
    gdf,
    style_function=lambda feature: {
        "fillColor": colormap(feature["properties"]["valeur"]),
        "color": "black",
        "weight": 0.5,
        "fillOpacity": 0.7,
    },
    tooltip=folium.GeoJsonTooltip(fields=["nom", "valeur"], aliases=["Commune", "Valeur"]),
).add_to(m)

colormap.caption = "Intensité choisie"
colormap.add_to(m)

st_folium(m, width=1000, height=700)
