import streamlit as st
import pandas as pd
from utilities import (
    apply_theme, load_and_analyze_sensor_data, load_service_orders,
    check_authentication, has_page_access, render_sidebar, UPLOAD_DIR, get_parts_for_os
)
import os
import json

check_authentication()
render_sidebar()
has_page_access("6_Equipment_History")
apply_theme()

st.title("🔎 Histórico do Ativo")

df_analyzed = load_and_analyze_sensor_data()
df_os = load_service_orders()

if df_analyzed is not None:
    asset_list = sorted(df_analyzed['asset_id'].unique())
    selected_asset_id = st.selectbox("Selecione um ativo para ver seu histórico:", options=asset_list)

    if selected_asset_id:
        st.divider()
        st.header(f"Histórico para: {selected_asset_id}")

        st.subheader("Histórico de Ordens de Serviço")
        asset_os = df_os[df_os['asset_id'] == selected_asset_id].copy()

        if asset_os.empty:
            st.info("Nenhuma OS registrada para este ativo.")
        else:
            for index, row in asset_os.sort_values(by="creation_date", ascending=False).iterrows():
                with st.expander(f"**{row['os_id']}** - {row['reason']} ({row['creation_date'].strftime('%d/%m/%Y')})"):
                    # (Detalhes da OS como antes)
                    # ...
                    
                    st.markdown("**Peças Utilizadas:**")
                    used_parts_df = get_parts_for_os(row['os_id'])
                    if used_parts_df.empty:
                        st.caption("Nenhuma peça registrada.")
                    else:
                        st.dataframe(used_parts_df)
                    
                    st.markdown("**Anexos:**")
                    # (Lógica de anexos como antes)
                    # ...
        
        st.divider()
        st.subheader("Histórico de Alertas")
        asset_alerts = df_analyzed[(df_analyzed['asset_id'] == selected_asset_id) & (~df_analyzed['status'].str.contains('Normal'))].copy()

        if asset_alerts.empty:
            st.info("Nenhum alerta registrado para este ativo.")
        else:
            alerts_to_show = asset_alerts[['timestamp', 'status', 'status_reason']].rename(
                columns={'timestamp': 'Data/Hora', 'status': 'Status', 'status_reason': 'Motivo'}
            )
            st.dataframe(alerts_to_show.sort_values(by="Data/Hora", ascending=False), use_container_width=True)