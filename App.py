import streamlit as st
from utilities import apply_theme, render_sidebar, validate_login, load_roles

st.set_page_config(page_title="Sistema de Gestão", layout="wide")
apply_theme()

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if st.session_state['authenticated']:
    render_sidebar()
    if st.session_state.get('just_logged_in', False):
        del st.session_state.just_logged_in 
        ROLES = load_roles()
        user_role = st.session_state['role']
        allowed_pages = ROLES.get(user_role, {}).get('pages', [])
        if allowed_pages:
            first_page_filename = allowed_pages[0]
            st.switch_page(f"pages/{first_page_filename}.py")
        else:
            st.error("Seu perfil não tem permissão para acessar nenhuma página.")
    st.title("Sistema de Gestão da Manutenção")
    st.header("Navegue pelas páginas no menu à esquerda para iniciar.")
else:
    st.header("Login do Sistema")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    if st.button("Login"):
        validate_login(username, password)
        if st.session_state.get('authenticated', False):
            st.session_state.just_logged_in = True
            st.rerun()