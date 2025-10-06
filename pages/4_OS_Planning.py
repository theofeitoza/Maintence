import streamlit as st
import pandas as pd
from utilities import (
    apply_theme, load_service_orders, append_to_table, update_os, load_users,
    load_and_analyze_sensor_data, add_resolved_alert, check_authentication, has_page_access, render_sidebar
)
from datetime import datetime
import numpy as np
import json
import uuid

check_authentication()
render_sidebar()
has_page_access("4_OS_Planning")
apply_theme()

st.title("📋 Planejamento e Gestão de OS")

df_analyzed = load_and_analyze_sensor_data()
df_os = load_service_orders()
users = load_users()
technician_names = ["Não atribuído"] + [details['name'] for user, details in users.items()]

st.subheader("Criar Nova Ordem de Serviço Manual")
with st.form(key="new_os_form", clear_on_submit=True):
    all_assets = df_analyzed['asset_id'].unique() if df_analyzed is not None else []
    col1, col2, col3, col4 = st.columns(4);
    with col1: selected_asset = st.selectbox("Selecione o Ativo:", options=all_assets)
    with col2: os_class = st.selectbox("Classe da OS:", options=["Preventiva", "Corretiva"], key="os_class")
    with col3: os_priority = st.selectbox("Prioridade:", options=["Baixa", "Média", "Alta", "Crítica"])
    with col4: assigned_technician = st.selectbox("Atribuir para:", options=technician_names)
    
    col_rec, col_cost = st.columns(2)
    os_recurrence = "Não recorrente"
    if os_class == "Preventiva":
        with col_rec: os_recurrence = st.selectbox("Recorrência:", options=["Não recorrente", "Semanalmente", "Mensalmente", "Trimestralmente", "Semestralmente", "Anualmente"])
    with col_cost: estimated_cost = st.number_input("Custo Estimado (R$)", min_value=0.0, format="%.2f")
    
    os_reason = st.text_area("Descrição do Serviço:")
    if st.form_submit_button("Criar OS"):
        if not os_reason or not selected_asset:
            st.warning("Por favor, preencha todos os campos obrigatórios (Ativo e Descrição).")
        else:
            new_os_id = f"OS-{uuid.uuid4().hex[:12]}"
            asset_type = df_analyzed[df_analyzed['asset_id'] == selected_asset]['asset_type'].iloc[0]
            
            # --- CORREÇÃO: Removida a coluna 'parts_used' ---
            new_os = pd.DataFrame([{'os_id': new_os_id, 'asset_id': selected_asset, 'asset_type': asset_type, 'creation_date': datetime.now(), 'reason': os_reason, 'priority': os_priority, 'status': 'Aberta', 'class': os_class, 'recorrencia': os_recurrence, 'assigned_to': assigned_technician, 'notes': '', 'estimated_cost': estimated_cost, 'actual_cost': 0.0, 'files_attached': '[]', 'completion_date': pd.NaT}])
            
            append_to_table(new_os, "service_orders")
            st.success(f"Ordem de Serviço {new_os_id} ({os_class}) criada com sucesso!")
            st.rerun()

st.header("Ordens de Serviço Atuais")
# --- CORREÇÃO: Filtros que permitem ao gestor ver TUDO ---
status_filter = st.multiselect('Filtrar por Status:', options=df_os['status'].unique(), default=df_os['status'].unique(), key="status_filter_full")
class_filter = st.multiselect('Filtrar por Classe:', options=df_os['class'].unique(), default=df_os['class'].unique(), key="class_filter_full")

df_os_filtered = df_os[df_os['status'].isin(status_filter) & df_os['class'].isin(class_filter)]
st.dataframe(df_os_filtered, use_container_width=True)