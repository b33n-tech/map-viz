import streamlit as st
import geopandas as gpd
import folium
from branca.colormap import linear
from streamlit_folium import st_folium

# ---- CONFIG ----
st.set_page_config(layout="wide")
st.title("🎨 Carte interactive - Coloration manuelle des communes du Bas-Rhin")

# ---- Charger GeoJSON depuis GitHub ----
@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/b33n-tech/map-viz/main/communes-67-bas-rhin.geojson"
    return gpd.read_file(url)

gdf = load_geojson()
gdf['code'] = gdf['code'].astype(str)

# ---- Sélection des communes à colorier ----
communes = gdf[['nom', 'code']].sort_values('nom')
selected_communes = st.multiselect("🧭 Choisis les communes à colorier :", communes['nom'])

# ---- Choix des intensités ----
custom_values = {}
for name in selected_communes:
    code = communes[communes['nom'] == name]['code'].values[0]
    value = st.slider(f"🎛️ Intensité pour {name}", 0, 100, 50)
    custom_values[code] = value

# ---- Palette et niveau ----
available_palettes = ["YlOrRd", "YlGnBu", "OrRd", "PuBuGn", "BuPu", "Greens", "Blues", "Reds", "Purples"]
palette = st.selectbox("🎨 Palette de couleurs", available_palettes)
n_classes = st.slider("📊 Nombre de niveaux", 2, 15, 10)

# ---- Appliquer les valeurs ----
gdf['valeur'] = gdf['code'].map(custom_values).fillna(0)

# ---- Générer la carte ----
m = folium.Map(location=[48.6, 7.6], zoom_start=9, tiles="cartodbpositron")

try:
    colormap_fn = getattr(linear, palette)
    colormap = colormap_fn.scale(gdf['valeur'].min(), gdf['valeur'].max()).to_step(n=n_classes)
except AttributeError:
    st.error(f"Palette '{palette}' non disponible")
    st.stop()

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

colormap.caption = "Valeurs manuelles"
colormap.add_to(m)

st_folium(m, width=1000, height=700)
