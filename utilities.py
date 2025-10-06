import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine, text
from passlib.context import CryptContext
import uuid # <-- NOVA IMPORTAÇÃO

# --- CONFIGURAÇÃO E CONSTANTES ---
DB_FILE = "maintenance.db"
engine = create_engine(f"sqlite:///{DB_FILE}")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
UPLOAD_DIR = "uploads"

AVAILABLE_PAGES = {
    "Tela Inicial": "1_Inicial_Screen",
    "Mapa da Planta": "2_Plant_Map",
    "Monitoramento de Equipamento": "3_Equipment_Monitoring",
    "Planejamento de OS": "4_OS_Planning",
    "Execução de OS": "5_Tech_App",
    "Histórico de Equipamento": "6_Equipment_History",
    "Gerenciamento de Usuário": "7_User_Management",
    "KPIs de Manutenção": "8_KPIs_Manutencao",
    "Gestão de Estoque": "9_Inventory_Management",
    "Gestão de Ativos": "10_Equipments_Management",
    "Previsão de Falhas": "11_Failure_Prediction"
}

ROOT_CAUSES = [
    "Não Definida", "Desgaste Natural", "Falha de Componente Elétrico",
    "Falha de Componente Mecânico", "Falta de Lubrificação", "Erro de Operação",
    "Sobrecarga", "Problema de Software/CLP", "Outros"
]

perfil_rotativo_pesado = {'params': {'vibracao': {'mean': 2.5, 'std': 0.5, 'op_min': 0, 'op_max': 5.0, 'warn_factor': 1.5, 'crit_factor': 2.0}, 'temperatura': {'mean': 80, 'std': 10, 'op_min': 40, 'op_max': 100, 'warn_factor': 1.1, 'crit_factor': 1.2}}}
perfil_rotativo_leve = {'params': {'vibracao': {'mean': 1.2, 'std': 0.3, 'op_min': 0, 'op_max': 3.0, 'warn_factor': 1.5, 'crit_factor': 2.2}, 'temperatura': {'mean': 65, 'std': 5, 'op_min': 30, 'op_max': 80, 'warn_factor': 1.1, 'crit_factor': 1.25}}}
perfil_processo_termico = {'params': {'pressao': {'mean': 15, 'std': 2, 'op_min': 5, 'op_max': 25, 'warn_factor': 1.2, 'crit_factor': 1.5}, 'temperatura': {'mean': 250, 'std': 25, 'op_min': 150, 'op_max': 300, 'warn_factor': 1.15, 'crit_factor': 1.25}}}
perfil_processo_hidraulico = {'params': {'pressao': {'mean': 150, 'std': 20, 'op_min': 100, 'op_max': 200, 'warn_factor': 1.1, 'crit_factor': 1.2}, 'vazao_oleo': {'mean': 40, 'std': 5, 'op_min': 30, 'op_max': 50, 'warn_factor': 1.2, 'crit_factor': 1.4}}}
perfil_eletronico = {'params': {'temperatura': {'mean': 55, 'std': 5, 'op_min': 25, 'op_max': 75, 'warn_factor': 1.1, 'crit_factor': 1.2}, 'corrente_eletrica': {'mean': 5, 'std': 1, 'op_min': 1, 'op_max': 10, 'warn_factor': 1.5, 'crit_factor': 2.0}}}

ASSET_PROFILES = {
    "Torno CNC": perfil_rotativo_pesado, "Fresadora": perfil_rotativo_pesado, "Compressor de Ar Industrial": perfil_processo_hidraulico,
    "Prensa Hidráulica": perfil_processo_hidraulico, "Caldeira a Vapor": perfil_processo_termico, "Gerador de Energia a Diesel": perfil_rotativo_pesado,
    "Robô de Soldagem": perfil_eletronico, "Esteira Transportadora": perfil_rotativo_leve, "Empilhadeira": perfil_rotativo_leve,
    "Trocador de Calor": perfil_processo_termico, "Bomba Centrífuga": perfil_rotativo_leve, "Forno de Indução": perfil_processo_termico,
    "Misturador Industrial": perfil_rotativo_pesado, "Reator Químico": perfil_processo_termico, "Máquina de Injeção de Plástico": perfil_processo_hidraulico,
    "Sistema de Filtração Industrial": perfil_processo_hidraulico, "Célula de Carga": perfil_eletronico, "Ponte Rolante": perfil_rotativo_pesado,
    "Extrusora": perfil_processo_hidraulico, "CLP": perfil_eletronico, "Máquina de Corte a Laser": perfil_processo_termico,
    "Dobradeira de Chapas": perfil_processo_hidraulico, "Torre de Resfriamento": perfil_processo_termico, "Moinho de Bolas": perfil_rotativo_pesado,
    "Secador Industrial": perfil_processo_termico, "Guilhotina Industrial": perfil_processo_hidraulico, "Autoclave Industrial": perfil_processo_termico,
    "Sistema de Visão Computacional": perfil_eletronico, "Chiller Industrial": perfil_processo_termico, "Silo de Armazenamento": perfil_processo_hidraulico
}

# --- FUNÇÃO DE INICIALIZAÇÃO DO BANCO DE DADOS (CORRIGIDA) ---
def initialize_database(clear_all=False):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with engine.connect() as conn:
        # --- CORREÇÃO DE ORDEM ---
        # 1. Garante que TODAS as tabelas existam
        conn.execute(text("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT NOT NULL, role TEXT NOT NULL, name TEXT NOT NULL)"))
        conn.execute(text("CREATE TABLE IF NOT EXISTS roles (role_name TEXT PRIMARY KEY, pages TEXT NOT NULL)"))
        conn.execute(text("CREATE TABLE IF NOT EXISTS assets (asset_id TEXT PRIMARY KEY, asset_type TEXT, location TEXT, description TEXT, install_date DATE)"))
        conn.execute(text("CREATE TABLE IF NOT EXISTS parts (part_id TEXT PRIMARY KEY, description TEXT, stock_quantity INTEGER, min_stock_level INTEGER DEFAULT 5, unit_cost REAL)"))
        conn.execute(text("CREATE TABLE IF NOT EXISTS service_orders (os_id TEXT PRIMARY KEY, asset_id TEXT, asset_type TEXT, creation_date DATETIME, reason TEXT, priority TEXT, status TEXT, class TEXT, recorrencia TEXT, assigned_to TEXT, notes TEXT, estimated_cost REAL, actual_cost REAL, files_attached TEXT, root_cause TEXT, completion_date DATETIME )"))
        conn.execute(text("CREATE TABLE IF NOT EXISTS os_parts_usage (usage_id INTEGER PRIMARY KEY AUTOINCREMENT, os_id TEXT, part_id TEXT, quantity_used INTEGER, FOREIGN KEY (os_id) REFERENCES service_orders(os_id), FOREIGN KEY (part_id) REFERENCES parts(part_id))"))
        conn.execute(text("CREATE TABLE IF NOT EXISTS resolved_alerts (asset_id TEXT, reason TEXT, PRIMARY KEY (asset_id, reason))"))
        conn.execute(text("CREATE TABLE IF NOT EXISTS sensor_data (timestamp DATETIME, asset_id TEXT, asset_type TEXT, location TEXT, latitude REAL, longitude REAL, temperatura REAL, pressao REAL, vibracao REAL, corrente_eletrica REAL, vazao_oleo REAL)"))

        # 2. Se `clear_all` for verdadeiro, AGORA podemos limpar as tabelas com segurança
        if clear_all:
            print("Limpando tabelas de dados operacionais...")
            conn.execute(text("DELETE FROM assets"))
            conn.execute(text("DELETE FROM sensor_data"))
            conn.execute(text("DELETE FROM service_orders"))
            conn.execute(text("DELETE FROM resolved_alerts"))
            conn.execute(text("DELETE FROM os_parts_usage"))
        
        # 3. Cria índices
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_os_asset_id ON service_orders (asset_id)"))
        
        # 4. Insere dados padrão (apenas na primeira execução de todas)
        if conn.execute(text("SELECT COUNT(*) FROM users")).scalar() == 0:
            pd.DataFrame([{"username": "admin", "password": hash_password("123"), "role": "admin", "name": "Administrador"},{"username": "user", "password": hash_password("123"), "role": "viewer", "name": "Operador"}]).to_sql("users", conn, if_exists='append', index=False)
        if conn.execute(text("SELECT COUNT(*) FROM roles")).scalar() == 0:
            pd.DataFrame([
                {"role_name": "admin", "pages": json.dumps(list(AVAILABLE_PAGES.values()))},
                {"role_name": "viewer", "pages": json.dumps(["1_Inicial_Screen", "2_Plant_Map", "3_Equipment_Monitoring", "6_Equipment_History", "8_KPIs_Manutencao", "11_previsao_de_falhas"])}
            ]).to_sql("roles", conn, if_exists='append', index=False)
        
        conn.commit()

# (O resto do arquivo é idêntico à versão estável anterior, completo abaixo)
DARK_THEME_CSS = """<style>...</style>""" # O CSS é mantido
def apply_theme(): st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)
def hash_password(password: str) -> str: return pwd_context.hash(password)
def verify_password(plain_password: str, hashed_password: str) -> bool: return pwd_context.verify(plain_password, hashed_password)
def load_users():
    initialize_database(); df = pd.read_sql("SELECT * FROM users", engine); return df.set_index('username').to_dict('index')
def save_users(users_data):
    for user, data in users_data.items():
        if data.get('password') and not data['password'].startswith('$2b$'): users_data[user]['password'] = hash_password(data['password'])
    df = pd.DataFrame.from_dict(users_data, orient='index').reset_index().rename(columns={'index': 'username'}); df.to_sql("users", engine, if_exists='replace', index=False)
def load_roles():
    initialize_database(); df = pd.read_sql("SELECT * FROM roles", engine)
    return {row['role_name']: {'pages': json.loads(row['pages'])} for _, row in df.iterrows()}
def save_roles(roles_data):
    df = pd.DataFrame([{'role_name': r, 'pages': json.dumps(p.get('pages',[]))} for r,p in roles_data.items()]); df.to_sql("roles", engine, if_exists='replace', index=False)
def validate_login(username, password):
    USERS = load_users(); user_data = USERS.get(username.lower())
    if user_data and verify_password(password, user_data['password']):
        st.session_state.update({'authenticated': True, 'username': username.lower(), 'role': user_data['role'], 'name': user_data['name']})
    else: st.error("Usuário ou senha incorretos.")
def check_authentication():
    if not st.session_state.get('authenticated', False): st.switch_page("App.py")
def has_page_access(page_filename):
    if 'role' not in st.session_state or st.session_state['role'] is None: st.switch_page("App.py")
    ROLES = load_roles(); user_role = st.session_state['role']
    if user_role not in ROLES: st.error("Perfil não encontrado."); st.stop()
    allowed_pages = ROLES[user_role].get('pages', []);
    if page_filename not in allowed_pages: st.error("🚫 Acesso negado."); st.stop()
def logout():
    st.session_state.clear(); st.rerun()
def render_sidebar():
    with st.sidebar:
        st.title(f"Bem-vindo, {st.session_state.get('name', '')}!"); st.write(f"**Perfil:** {st.session_state.get('role', '')}")
        if st.button("Logout"): logout()
def append_to_table(df, table_name):
    df.to_sql(table_name, engine, if_exists='append', index=False)
    
def update_os(os_id, new_status, notes, actual_cost, root_cause, completion_date=None):
    """Função 'cirúrgica' para ATUALIZAR uma OS com todos os campos, incluindo a causa raiz."""
    with engine.connect() as conn:
        stmt = text("""
            UPDATE service_orders 
            SET status = :status, notes = :notes, actual_cost = :actual_cost,
                root_cause = :root_cause, completion_date = :completion_date 
            WHERE os_id = :os_id
        """)
        conn.execute(stmt, {
            "status": new_status, "notes": notes, "actual_cost": actual_cost,
            "root_cause": root_cause, "completion_date": completion_date, "os_id": os_id
        })
        conn.commit()

def add_attachment_to_os(os_id, filename):
    with engine.connect() as conn:
        current_files_json = conn.execute(text("SELECT files_attached FROM service_orders WHERE os_id = :os_id"), {"os_id": os_id}).scalar()
        current_files = json.loads(current_files_json) if current_files_json and pd.notna(current_files_json) else []
        if filename not in current_files:
            current_files.append(filename); new_files_json = json.dumps(current_files)
            stmt = text("UPDATE service_orders SET files_attached = :files WHERE os_id = :os_id")
            conn.execute(stmt, {"files": new_files_json, "os_id": os_id}); conn.commit()
@st.cache_data
def load_and_analyze_sensor_data():
    try:
        df = pd.read_sql("SELECT * FROM sensor_data", engine, parse_dates=['timestamp']); return apply_alert_rules(df)
    except Exception:
        st.error("Tabela 'sensor_data' não encontrada. Execute 'gerador_dados_planta.py' primeiro."); return None
def load_service_orders():
    initialize_database(); return pd.read_sql("SELECT * FROM service_orders", engine, parse_dates=['creation_date', 'completion_date'])
def add_resolved_alert(asset_id, reason):
    new_entry = pd.DataFrame([{'asset_id': asset_id, 'reason': reason}])
    try: new_entry.to_sql("resolved_alerts", engine, if_exists='append', index=False)
    except: pass
def suppress_resolved_alerts(df_analyzed):
    df_resolved = pd.read_sql("SELECT * FROM resolved_alerts", engine).drop_duplicates()
    if df_resolved.empty: return df_analyzed
    df_analyzed['alert_key'] = df_analyzed['asset_id'] + "_" + df_analyzed['status_reason']; df_resolved['alert_key'] = df_resolved['asset_id'] + "_" + df_resolved['reason']
    resolved_mask = df_analyzed['alert_key'].isin(df_resolved['alert_key'])
    df_analyzed.loc[resolved_mask, 'status'] = 'Normal (Resolvido)'; df_analyzed.drop(columns=['alert_key'], inplace=True)
    return df_analyzed
def apply_alert_rules(df):
    df_alerts = df.copy(); df_alerts['status'] = 'Normal'; df_alerts['status_reason'] = ''
    for asset_type, profile in ASSET_PROFILES.items():
        if asset_type in df_alerts['asset_type'].unique():
            for param, rules in profile['params'].items():
                if param in df_alerts.columns and not df_alerts[df_alerts['asset_type']==asset_type][param].isnull().all():
                    crit_high=rules['op_max']*rules['crit_factor']; warn_high=rules['op_max']*rules['warn_factor']
                    crit_low=rules['op_min']/rules['crit_factor']; warn_low=rules['op_min']/rules['warn_factor']
                    is_type = (df_alerts['asset_type'] == asset_type)
                    df_alerts.loc[is_type & (df_alerts[param] > crit_high), ['status', 'status_reason']] = ['Crítico',f'{param.title()} Alta']; df_alerts.loc[is_type & (df_alerts[param] < crit_low), ['status', 'status_reason']] = ['Crítico',f'{param.title()} Baixa']; df_alerts.loc[is_type & (df_alerts[param] > warn_high) & (df_alerts[param] <= crit_high), ['status', 'status_reason']] = ['Atenção',f'{param.title()} Alta']; df_alerts.loc[is_type & (df_alerts[param] < warn_low) & (df_alerts[param] >= crit_low), ['status', 'status_reason']] = ['Atenção',f'{param.title()} Baixa']
    return df_alerts
def check_and_generate_os(df_analyzed, df_os):
    critical_problems = df_analyzed[df_analyzed['status'] == 'Crítico'][['asset_id', 'asset_type', 'status_reason']].drop_duplicates()
    new_os_list = []
    for _, problem in critical_problems.iterrows():
        has_active_os = not df_os[(df_os['asset_id'] == problem['asset_id']) & (df_os['reason'] == problem['status_reason']) & (df_os['status'].isin(['Aberta', 'Em Andamento']))].empty
        if not has_active_os:
            new_os_list.append({'os_id': f"OS-{uuid.uuid4().hex[:12]}", 'asset_id': problem['asset_id'], 'asset_type': problem['asset_type'], 'creation_date': datetime.now(), 'reason': problem['status_reason'], 'priority': 'Crítica', 'status': 'Aberta', 'class': 'Preditiva', 'recorrencia': 'Não recorrente', 'assigned_to': 'Não atribuído', 'notes': '', 'estimated_cost': 0.0, 'actual_cost': 0.0, 'files_attached': json.dumps([]), 'completion_date': pd.NaT})
    if new_os_list:
        df_new_os = pd.DataFrame(new_os_list); append_to_table(df_new_os, "service_orders"); st.toast("Novas OS Preditivas foram geradas!", icon="✅")
        return pd.concat([df_os, df_new_os], ignore_index=True)
    return df_os

def check_and_generate_recurring_os(df_os):
    recurrence_map = {'Semanalmente': relativedelta(weeks=1), 'Mensalmente': relativedelta(months=1), 'Trimestralmente': relativedelta(months=3), 'Semestralmente': relativedelta(months=6), 'Anualmente': relativedelta(years=1)}
    preventive_completed = df_os[(df_os['class'] == 'Preventiva') & (df_os['recorrencia'] != 'Não recorrente') & (df_os['status'] == 'Concluída')].copy()
    if preventive_completed.empty: return df_os
    new_os_list = []
    for _, group in preventive_completed.groupby(['asset_id', 'reason']):
        last_os = group.sort_values(by='completion_date', ascending=False).iloc[0]
        period = recurrence_map.get(last_os['recorrencia'])
        if period and datetime.now() >= (last_os['completion_date'] + period):
            has_open_os = not df_os[(df_os['asset_id'] == last_os['asset_id']) & (df_os['reason'] == last_os['reason']) & (df_os['status'] == 'Aberta')].empty
            if not has_open_os:
                # --- CORREÇÃO: Usa uuid para garantir um ID único ---
                new_os_id = f"OS-{uuid.uuid4().hex[:12]}"
                new_os_list.append({'os_id': new_os_id, 'asset_id': last_os['asset_id'], 'asset_type': last_os['asset_type'], 'creation_date': datetime.now(), 'reason': last_os['reason'], 'priority': last_os['priority'], 'status': 'Aberta', 'class': 'Preventiva', 'recorrencia': last_os['recorrencia'], 'assigned_to': last_os['assigned_to'], 'notes': '', 'estimated_cost': last_os['estimated_cost'], 'actual_cost': 0.0, 'parts_used': '', 'files_attached': json.dumps([]), 'completion_date': pd.NaT})
    if new_os_list:
        df_new_os = pd.DataFrame(new_os_list)
        append_to_table(df_new_os, "service_orders")
        st.toast(f"{len(new_os_list)} nova(s) OS Preventiva(s) gerada(s)!", icon="🗓️")
        return pd.concat([df_os, df_new_os], ignore_index=True)
    return df_os

@st.cache_data
def load_parts():
    initialize_database(); return pd.read_sql("SELECT * FROM parts", engine)
def save_parts(df_parts):
    df_parts.to_sql("parts", engine, if_exists='replace', index=False)
@st.cache_data
def load_assets():
    initialize_database(); return pd.read_sql("SELECT * FROM assets", engine, parse_dates=['install_date'])
def save_assets(df_assets):
    df_assets.to_sql("assets", engine, if_exists='replace', index=False)
def add_part_to_os(os_id, part_id, quantity):
    with engine.connect() as conn:
        stock_quantity = conn.execute(text("SELECT stock_quantity FROM parts WHERE part_id = :part_id"), {"part_id": part_id}).scalar()
        if stock_quantity is None or stock_quantity < quantity:
            st.error(f"Estoque insuficiente para a peça {part_id}. Disponível: {stock_quantity or 0}"); return False
        usage_df = pd.DataFrame([{"os_id": os_id, "part_id": part_id, "quantity_used": quantity}])
        append_to_table(usage_df, "os_parts_usage")
        new_quantity = stock_quantity - quantity
        stmt = text("UPDATE parts SET stock_quantity = :new_qty WHERE part_id = :part_id")
        conn.execute(stmt, {"new_qty": new_quantity, "part_id": part_id}); conn.commit()
        st.success(f"{quantity} unidade(s) de '{part_id}' adicionada(s) à OS."); return True
@st.cache_data
def get_parts_for_os(os_id):
    query = "SELECT T2.description, T1.quantity_used, T2.unit_cost FROM os_parts_usage AS T1 JOIN parts AS T2 ON T1.part_id = T2.part_id WHERE T1.os_id = ?"
    return pd.read_sql(query, engine, params=(os_id,))