import streamlit as st
from utilities import (
    apply_theme, load_service_orders, update_os, add_attachment_to_os, UPLOAD_DIR,
    add_resolved_alert, check_authentication, has_page_access, render_sidebar,
    load_parts, add_part_to_os, get_parts_for_os, ROOT_CAUSES
)
from datetime import datetime
import os
import json
import pandas as pd

check_authentication(); render_sidebar(); has_page_access("5_Tech_App"); apply_theme()

st.title("⚙️ Execução de Ordens de Serviço")
df_os = load_service_orders(); df_parts = load_parts()
current_user_name = st.session_state['name']

st.header("Minhas Tarefas (OS Abertas / Em Andamento)")
my_os_filter = (df_os['status'].isin(['Aberta', 'Em Andamento']))
if st.session_state['role'] != 'admin':
    my_os_filter &= (df_os['assigned_to'] == current_user_name)
my_os = df_os[my_os_filter]
if st.session_state['role'] == 'admin':
    if st.toggle("Ver todas as OS ativas (visão de admin)"):
        my_os = df_os[df_os['status'].isin(['Aberta', 'Em Andamento'])]
st.dataframe(my_os, use_container_width=True)

st.header("Detalhes e Atualização de OS")
os_to_update_options = my_os['os_id'].tolist()
if not os_to_update_options:
    st.info("Não há ordens de serviço para atualizar.")
else:
    selected_os_id = st.selectbox("Selecione a OS para trabalhar:", options=os_to_update_options)
    os_row = df_os[df_os['os_id'] == selected_os_id].iloc[0]
    st.write(f"**Ativo:** {os_row['asset_id']} | **Descrição:** {os_row['reason']}")
    
    tab1, tab2, tab3 = st.tabs(["Atualizar Status", "Registrar Peças", "Anexos"])

    with tab1:
        with st.form("update_os_form"):
            st.subheader("Atualizar Status, Custos e Causa Raiz")
            new_status = st.selectbox("Novo Status:", options=['Em Andamento', 'Concluída'], index=['Em Andamento', 'Concluída'].index(os_row['status']) if os_row['status'] in ['Em Andamento', 'Concluída'] else 0)
            actual_cost = st.number_input("Custo de Mão de Obra (R$)", min_value=0.0, format="%.2f", value=float(os_row.get('actual_cost', 0.0)))
            notes = st.text_area("Observações da Execução:", value=os_row.get('notes', ''))
            
            # --- CORREÇÃO: Campo de Causa Raiz agora está sempre visível ---
            current_cause = os_row.get('root_cause')
            default_index = ROOT_CAUSES.index(current_cause) if current_cause in ROOT_CAUSES else 0
            root_cause = st.selectbox(
                "Causa Raiz da Falha:", 
                options=ROOT_CAUSES, 
                index=default_index,
                help="Selecione a causa principal da falha. Obrigatório ao concluir a OS."
            )

            if st.form_submit_button("Salvar Atualização"):
                # A verificação de obrigatoriedade acontece apenas no momento do envio
                if new_status == 'Concluída' and (root_cause is None or root_cause == "Não Definida"):
                    st.error("Por favor, selecione uma Causa Raiz antes de concluir a Ordem de Serviço.")
                else:
                    completion_date = datetime.now() if new_status == 'Concluída' else None
                    # Se o status não for 'Concluída', a causa raiz não é alterada se não foi definida
                    final_root_cause = root_cause if new_status == 'Concluída' else os_row.get('root_cause', root_cause)
                    
                    update_os(selected_os_id, new_status, notes, actual_cost, final_root_cause, completion_date)
                    
                    if new_status == 'Concluída' and os_row['class'] == 'Preditiva':
                        add_resolved_alert(os_row['asset_id'], os_row['reason'])
                        
                    st.success(f"Ordem de Serviço {selected_os_id} atualizada!")
                    st.rerun()

    with tab2: # REGISTRAR PEÇAS
        st.subheader("Registrar Uso de Peças")
        st.write("**Peças já utilizadas nesta OS:**")
        used_parts_df = get_parts_for_os(selected_os_id)
        if used_parts_df.empty:
            st.caption("Nenhuma peça registrada.")
        else:
            st.dataframe(used_parts_df, use_container_width=True)

        with st.form("add_part_form"):
            col1, col2 = st.columns(2)
            with col1:
                part_to_add = st.selectbox("Selecione a peça:", options=df_parts['part_id'].unique())
            with col2:
                quantity_to_add = st.number_input("Quantidade utilizada:", min_value=1, step=1)
            
            if st.form_submit_button("Adicionar Peça"):
                add_part_to_os(selected_os_id, part_to_add, quantity_to_add)
                st.rerun()

    with tab3: # ANEXOS
        st.subheader("Anexos")
        files_attached_json = os_row.get('files_attached')
        files_attached = json.loads(files_attached_json) if files_attached_json and pd.notna(files_attached_json) else []
        if not files_attached:
            st.caption("Nenhum anexo para esta OS.")
        else:
            for filename in files_attached:
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        st.download_button(f"📄 Baixar {filename}", f.read(), file_name=filename, key=f"download_{os_row['os_id']}_{filename}")
        
        uploaded_files = st.file_uploader("Carregar novos anexos", accept_multiple_files=True, key=f"uploader_{selected_os_id}")
        if uploaded_files:
            for uploaded_file in uploaded_files:
                save_filename = f"{selected_os_id}_{uploaded_file.name}"
                save_path = os.path.join(UPLOAD_DIR, save_filename)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                add_attachment_to_os(selected_os_id, save_filename)
            st.success(f"{len(uploaded_files)} arquivo(s) anexado(s)!")
            st.rerun()