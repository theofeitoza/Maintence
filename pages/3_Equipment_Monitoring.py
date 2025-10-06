import streamlit as st
import plotly.express as px
from utilities import apply_theme, load_and_analyze_sensor_data, check_authentication, has_page_access, render_sidebar
import numpy as np

check_authentication()
render_sidebar()
has_page_access("3_Equipment_Monitoring")
apply_theme()

st.title("📊 Análise Detalhada por Ativo")

df_analyzed = load_and_analyze_sensor_data()
if df_analyzed is not None:
    selected_asset_id = st.selectbox('Selecione um Ativo:', options=df_analyzed['asset_id'].unique())
    if selected_asset_id:
        df_asset_detail = df_analyzed[df_analyzed['asset_id'] == selected_asset_id]
        st.subheader(f"Dados do Ativo: {selected_asset_id}")
        sensor_cols_detail = [c for c in df_asset_detail.select_dtypes(include=np.number).columns if c not in ['latitude', 'longitude']]
        for sensor in sensor_cols_detail:
            fig = px.line(df_asset_detail, x='timestamp', y=sensor, 
                          title=f'Leituras de {sensor.replace("_", " ").title()}',
                          template='plotly_dark')
            alerts_warn = df_asset_detail[df_asset_detail['status'] == 'Atenção']
            alerts_crit = df_asset_detail[df_asset_detail['status'] == 'Crítico']
            if not alerts_warn.empty: fig.add_scatter(x=alerts_warn['timestamp'], y=alerts_warn[sensor], mode='markers', name='Atenção', marker=dict(color='orange', size=8, symbol='triangle-up'))
            if not alerts_crit.empty: fig.add_scatter(x=alerts_crit['timestamp'], y=alerts_crit[sensor], mode='markers', name='Crítico', marker=dict(color='red', size=8, symbol='x'))
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{sensor}_{selected_asset_id}")