import streamlit as st
import pandas as pd
from utilities import apply_theme, load_parts, save_parts, check_authentication, has_page_access, render_sidebar

check_authentication()
render_sidebar()
has_page_access("9_Inventory_Management")
apply_theme()

st.title("📦 Gestão de Estoque de Peças")

df_parts = load_parts()

# --- ALERTA DE ESTOQUE BAIXO ---
low_stock_parts = df_parts[df_parts['stock_quantity'] <= df_parts['min_stock_level']]
if not low_stock_parts.empty:
    st.warning("⚠️ Alerta de Estoque Baixo para os seguintes itens:")
    st.dataframe(low_stock_parts)

with st.expander("➕ Adicionar/Editar Peça no Inventário"):
    with st.form("part_form", clear_on_submit=True):
        part_id = st.text_input("ID da Peça (SKU)")
        description = st.text_input("Descrição da Peça")
        col1, col2, col3 = st.columns(3)
        with col1: stock_quantity = st.number_input("Quantidade em Estoque", min_value=0, step=1)
        with col2: min_stock_level = st.number_input("Nível Mínimo de Estoque", min_value=0, step=1)
        with col3: unit_cost = st.number_input("Custo Unitário (R$)", min_value=0.0, format="%.2f")
        
        if st.form_submit_button("Salvar Peça"):
            if not all([part_id, description]):
                st.warning("ID da Peça e Descrição são obrigatórios.")
            else:
                if part_id in df_parts['part_id'].values:
                    df_parts.loc[df_parts['part_id'] == part_id, ['description', 'stock_quantity', 'min_stock_level', 'unit_cost']] = [description, stock_quantity, min_stock_level, unit_cost]
                    st.success(f"Peça '{part_id}' atualizada!")
                else:
                    new_part = pd.DataFrame([{'part_id': part_id, 'description': description, 'stock_quantity': stock_quantity, 'min_stock_level': min_stock_level, 'unit_cost': unit_cost}])
                    df_parts = pd.concat([df_parts, new_part], ignore_index=True)
                    st.success(f"Peça '{part_id}' adicionada!")
                save_parts(df_parts)
                st.rerun()

st.header("Inventário Atual de Peças")
st.dataframe(df_parts, use_container_width=True)