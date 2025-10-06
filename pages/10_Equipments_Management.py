import streamlit as st
import pandas as pd
from utilities import apply_theme, check_authentication, has_page_access, render_sidebar, load_assets, save_assets, ASSET_PROFILES
from datetime import datetime

check_authentication()
render_sidebar()
has_page_access("10_Equipments_Management")
apply_theme()

st.title("🔩 Gestão de Ativos")

df_assets = load_assets()

with st.expander("➕ Cadastrar Novo Ativo"):
    with st.form("asset_form", clear_on_submit=True):
        st.subheader("Detalhes do Ativo")
        asset_id = st.text_input("ID do Ativo (Ex: MOTOR-001)")
        asset_type = st.selectbox("Tipo de Ativo", options=list(ASSET_PROFILES.keys()))
        location = st.text_input("Localização (Ex: Setor A-Linha 2)")
        description = st.text_input("Descrição")
        install_date = st.date_input("Data de Instalação", value=datetime.today())
        
        if st.form_submit_button("Salvar Ativo"):
            if not all([asset_id, asset_type, location]):
                st.warning("ID, Tipo e Localização são obrigatórios.")
            elif asset_id in df_assets['asset_id'].values:
                st.error(f"O ID de ativo '{asset_id}' já existe.")
            else:
                new_asset = pd.DataFrame([{
                    'asset_id': asset_id, 'asset_type': asset_type, 'location': location,
                    'description': description, 'install_date': install_date
                }])
                df_assets = pd.concat([df_assets, new_asset], ignore_index=True)
                save_assets(df_assets)
                st.success(f"Ativo '{asset_id}' cadastrado com sucesso!")
                st.rerun()

st.header("Inventário de Ativos Cadastrados")
st.dataframe(df_assets, use_container_width=True)