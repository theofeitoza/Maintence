import streamlit as st
import pandas as pd
from utilities import (
    apply_theme, load_and_analyze_sensor_data, load_service_orders, load_parts,
    check_and_generate_os, suppress_resolved_alerts, check_and_generate_recurring_os,
    check_authentication, has_page_access, render_sidebar
)
check_authentication(); render_sidebar()
has_page_access("1_Inicial_Screen") # <-- CORRIGIDO
apply_theme()
st.title("🏭 Visão Geral da Planta")
df_parts = load_parts()
low_stock_parts = df_parts[df_parts['stock_quantity'] <= df_parts['min_stock_level']]
if not low_stock_parts.empty:
    st.warning(f"⚠️ **Alerta:** {len(low_stock_parts)} peça(s) com estoque baixo! Verifique a 'Gestão de Estoque'.")
df_analyzed_raw = load_and_analyze_sensor_data()
df_os = load_service_orders()
if df_analyzed_raw is not None:
    df_os = check_and_generate_recurring_os(df_os)
    df_analyzed = suppress_resolved_alerts(df_analyzed_raw)
    df_os = check_and_generate_os(df_analyzed, df_os)
    st.header("KPIs (Últimas 24 Horas)")
    max_timestamp = df_analyzed['timestamp'].max()
    cutoff_24h = max_timestamp - pd.Timedelta(hours=24)
    df_last_24h = df_analyzed[df_analyzed['timestamp'] >= cutoff_24h]
    total_assets = df_analyzed['asset_id'].nunique()
    assets_with_alerts_24h = df_last_24h[~df_last_24h['status'].str.contains('Normal')]['asset_id'].nunique()
    os_abertas_count = df_os[df_os['status'] == 'Aberta'].shape[0]
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Ativos", f"{total_assets}")
    col2.metric("Ativos com Alertas Ativos (24h)", f"{assets_with_alerts_24h}")
    col3.metric("Ordens de Serviço Abertas", f"{os_abertas_count}")
    st.header("Status dos Ativos (24h)")
    asset_status_summary = df_last_24h.groupby('asset_id').agg(
        asset_type=('asset_type', 'first'),
        location=('location', 'first'),
        status=('status', lambda x: 'Crítico' if 'Crítico' in x.values else ('Atenção' if 'Atenção' in x.values else ('Normal (Resolvido)' if 'Normal (Resolvido)' in x.values else 'Normal')))
    ).reset_index()
    def style_alert_rows(row):
        if row.status == 'Crítico': return ['background-color: #8B0000; color: white'] * len(row)
        if row.status == 'Atenção': return ['background-color: #FFD700; color: #31333F'] * len(row)
        if row.status == 'Normal (Resolvido)': return ['background-color: #006400; color: white'] * len(row)
        return [''] * len(row)
    st.dataframe(asset_status_summary.style.apply(style_alert_rows, axis=1), use_container_width=True)