import streamlit as st
import pandas as pd
from utilities import apply_theme, load_and_analyze_sensor_data, check_authentication, has_page_access, render_sidebar

check_authentication()
render_sidebar()
has_page_access("2_Plant_Map")
apply_theme()

st.title("🗺️ Mapa da Planta")

df_analyzed = load_and_analyze_sensor_data()
if df_analyzed is not None:
    asset_locations = df_analyzed[['asset_id', 'latitude', 'longitude']].drop_duplicates().set_index('asset_id')
    asset_status_summary_map = df_analyzed[df_analyzed['timestamp'] >= (df_analyzed['timestamp'].max() - pd.Timedelta(hours=1))].groupby('asset_id').agg(
        status=('status', lambda x: 'Crítico' if 'Crítico' in x.values else ('Atenção' if 'Atenção' in x.values else 'Normal'))
    ).reset_index().set_index('asset_id')
    map_data = asset_locations.join(asset_status_summary_map).reset_index()
    color_map = {'Normal': '#008000', 'Atenção': '#FFA500', 'Crítico': '#FF0000'}
    map_data['color'] = map_data['status'].map(color_map)
    map_data.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True)
    st.map(map_data, color='color', size=20)
    st.write("### Legenda")
    st.markdown("""
    - <span style="color:#008000">**Verde:**</span> Ativo em status Normal
    - <span style="color:#FFA500">**Laranja:**</span> Ativo em status de Atenção
    - <span style="color:#FF0000">**Vermelho:**</span> Ativo em status Crítico
    """, unsafe_allow_html=True)