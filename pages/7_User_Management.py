import streamlit as st
from utilities import apply_theme, check_authentication, has_page_access, load_users, save_users, load_roles, save_roles, AVAILABLE_PAGES, render_sidebar, hash_password

check_authentication(); render_sidebar()
has_page_access("7_User_Management") # <-- CORRIGIDO
apply_theme()

st.title("🔑 Administração do Sistema")

tab1, tab2 = st.tabs(["Gerenciar Usuários", "Gerenciar Perfis de Acesso"])

with tab1:
    st.header("Gerenciar Usuários")
    users_data = load_users()
    roles_data = load_roles()

    # --- Formulário de Cadastro de Novo Usuário (sem alterações) ---
    with st.expander("➕ Cadastrar Novo Usuário"):
        with st.form("new_user_form", clear_on_submit=True):
            st.subheader("Novo Usuário")
            new_username = st.text_input("Login do Usuário (ex: joao.silva)").lower()
            new_name = st.text_input("Nome Completo")
            new_password = st.text_input("Senha Temporária", type="password")
            new_role = st.selectbox("Perfil de Acesso", options=list(roles_data.keys()))
            
            if st.form_submit_button("Cadastrar Usuário"):
                if not all([new_username, new_name, new_password, new_role]):
                    st.warning("Todos os campos são obrigatórios.")
                elif new_username in users_data:
                    st.error(f"O login '{new_username}' já existe.")
                else:
                    hashed_password = hash_password(new_password)
                    users_data[new_username] = {"password": hashed_password, "role": new_role, "name": new_name}
                    save_users(users_data)
                    st.success(f"Usuário '{new_username}' cadastrado com sucesso!")
                    st.rerun()

    st.divider()
    
    # --- Seção para Editar Perfis (sem alterações) ---
    st.subheader("Alterar Perfil de Acesso de Usuários")
    for username, details in users_data.items():
        col1, col2 = st.columns([1, 1])
        with col1:
            st.write(f"**Usuário:** `{username}` | **Nome:** {details['name']}")
        with col2:
            available_roles = list(roles_data.keys())
            user_role = details.get('role', 'viewer')
            if user_role not in available_roles:
                current_role_index = 0 
            else:
                current_role_index = available_roles.index(user_role)
            is_current_user = (username == st.session_state['username'])
            new_role = st.selectbox(
                "Perfil", 
                options=available_roles, 
                index=current_role_index, 
                key=f"role_{username}", 
                disabled=is_current_user
            )
            users_data[username]['role'] = new_role
            if is_current_user:
                st.caption("Não é possível alterar o próprio perfil.")
    
    if st.button("Salvar Alterações de Perfis"):
        save_users(users_data)
        st.success("Perfis de usuário atualizados!")
        st.rerun()

    st.divider()
    # --- NOVA SEÇÃO: ALTERAR SENHA ---
    with st.expander("➕ Alterar Senha de Usuário"):
        with st.form("reset_password_form", clear_on_submit=True):
            user_to_reset = st.selectbox("Selecione o usuário para alterar a senha:", options=list(users_data.keys()))
            new_password_reset = st.text_input("Nova Senha", type="password", key="new_pass")
            confirm_password_reset = st.text_input("Confirmar Nova Senha", type="password", key="confirm_pass")

            if st.form_submit_button("Alterar Senha"):
                if not user_to_reset:
                    st.warning("Nenhum usuário selecionado.")
                elif not new_password_reset:
                    st.warning("O campo de nova senha não pode estar vazio.")
                elif new_password_reset != confirm_password_reset:
                    st.error("As senhas não coincidem. Tente novamente.")
                else:
                    # Carrega os dados mais recentes antes de alterar
                    current_users = load_users()
                    # Gera o hash da nova senha
                    hashed_password = hash_password(new_password_reset)
                    # Atualiza a senha do usuário selecionado
                    current_users[user_to_reset]['password'] = hashed_password
                    # Salva os dados atualizados no banco de dados
                    save_users(current_users)
                    st.success(f"Senha do usuário '{user_to_reset}' alterada com sucesso!")

    st.divider()
    st.warning("As senhas dos usuários são salvas de forma segura usando hashing. Não é possível recuperá-las, apenas redefini-las.")


with tab2:
    # (O código desta aba não precisa de alterações)
    st.header("Gerenciar Perfis de Acesso (Classes)")
    roles_data = load_roles()
    with st.expander("➕ Criar Novo Perfil de Acesso"):
        with st.form("new_role_form", clear_on_submit=True):
            new_role_name = st.text_input("Nome do Novo Perfil (ex: manutencao, engenharia)").lower()
            if st.form_submit_button("Criar Perfil"):
                if new_role_name and new_role_name not in roles_data:
                    roles_data[new_role_name] = {"pages": []}
                    save_roles(roles_data)
                    st.success(f"Perfil '{new_role_name}' criado com sucesso!"); st.rerun()
                else:
                    st.error("Nome de perfil inválido ou já existente.")
    
    st.divider()
    
    st.subheader("Permissões por Perfil")
    for role, permissions in roles_data.items():
        st.write(f"**Perfil:** `{role}`")
        is_admin_role = (role == 'admin')
        page_ids = list(AVAILABLE_PAGES.values())
        current_permissions = permissions.get('pages', [])
        selected_pages = st.multiselect(
            "Páginas autorizadas:", options=page_ids,
            format_func=lambda page_id: [name for name, id in AVAILABLE_PAGES.items() if id == page_id][0],
            default=current_permissions, key=f"pages_{role}", disabled=is_admin_role
        )
        if is_admin_role: st.caption("O perfil 'admin' tem acesso total e não pode ser editado.")
        roles_data[role]['pages'] = selected_pages
    
    if st.button("Salvar Alterações de Permissões"):
        save_roles(roles_data)
        st.success("Permissões dos perfis atualizadas com sucesso!")
        st.rerun()