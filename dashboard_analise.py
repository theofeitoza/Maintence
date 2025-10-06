import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
from datetime import datetime

st.set_page_config(page_title="Dashboard de Gestão de Ativos", layout="wide")

# (ASSET_PROFILES e as funções de lógica permanecem iguais)
ASSET_PROFILES = {
    'Caldeira': {
        'params': {
            'temperatura': {'op_min': 420, 'op_max': 480, 'warn_factor': 1.10, 'crit_factor': 1.15},
            'pressao':     {'op_min': 32, 'op_max': 38, 'warn_factor': 1.08, 'crit_factor': 1.12},
        }
    },
    'Motor Elétrico': {
        'params': {
            'vibracao':    {'op_min': 0, 'op_max': 2.5, 'warn_factor': 1.20, 'crit_factor': 1.50},
            'temperatura': {'op_min': 60, 'op_max': 95, 'warn_factor': 1.05, 'crit_factor': 1.10},
        }
    },
    'Prensa Hidráulica': {
        'params': {
            'pressao': {'op_min': 180, 'op_max': 220, 'warn_factor': 1.10, 'crit_factor': 1.20},
            'vazao_oleo': {'op_min': 45, 'op_max': 55, 'warn_factor': 1.15, 'crit_factor': 1.25},
        }
    }
}
OS_FILE_PATH = 'ordens_de_servico.csv'


# --- LÓGICA E CSS DO TEMA (COM ESTILOS PARA WIDGETS) ---

if 'theme' not in st.session_state:
    st.session_state.theme = "light"

# CSS para o tema escuro
dark_theme_css = """
<style>
    .stApp {
        background-color: #0E1117 !important;
        color: #FAFAFA !important;
    }
    h1, h2, h3, label, p, .st-emotion-cache-1y4p8pa, .st-emotion-cache-16idsys, .st-emotion-cache-1gulkj5  {
        color: #FAFAFA !important;
    }
    div[data-testid="stMetric"] {
        background-color: #262730 !important;
        border-radius: 0.5rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        color: #A0A0A0 !important;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #FAFAFA !important;
    }
    /* AJUSTE: Estilo para caixas de seleção (filtros) */
    div[data-testid="stSelectbox"] div[data-baseweb="select"],
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] {
        background-color: #262730 !important;
        color: #FAFAFA !important;
    }
</style>
"""
# CSS para o tema claro
light_theme_css = """
<style>
    .stApp {
        background-color: #FFFFFF !important;
        color: #31333F !important;
    }
    h1, h2, h3, label, p, .st-emotion-cache-1y4p8pa, .st-emotion-cache-16idsys, .st-emotion-cache-1gulkj5 {
        color: #31333F !important;
    }
    div[data-testid="stMetric"] {
        background-color: #F0F2F6 !important;
        border-radius: 0.5rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        color: #606060 !important;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #31333F !important;
    }
    /* AJUSTE: Estilo para caixas de seleção (filtros) */
    div[data-testid="stSelectbox"] div[data-baseweb="select"],
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] {
        background-color: #F0F2F6 !important;
        color: #31333F !important;
    }
</style>
"""

if st.session_state.theme == "dark":
    st.markdown(dark_theme_css, unsafe_allow_html=True)
else:
    st.markdown(light_theme_css, unsafe_allow_html=True)


# --- AJUSTE: FUNÇÃO DE ESTILO DE TABELA MAIS COMPLETA ---
def style_dataframe(df, theme):
    """Aplica o tema claro/escuro completo a um dataframe, incluindo cabeçalhos e índice."""
    if theme == 'dark':
        header_props = [('background-color', '#3C4254'), ('color', '#FAFAFA')]
        cell_props = [('background-color', '#262730'), ('color', '#FAFAFA')]
        hover_props = [('background-color', '#4A526B')]
    else: # light theme
        header_props = [('background-color', '#E6EAF1'), ('color', '#31333F')]
        cell_props = [('background-color', '#FFFFFF'), ('color', '#31333F')]
        hover_props = [('background-color', '#F0F2F6')]
        
    styler = df.style.set_table_styles([
        {'selector': 'thead th', 'props': header_props},
        {'selector': 'thead th:first-child', 'props': header_props}, # Coluna do índice
        {'selector': 'tbody tr:hover', 'props': hover_props},
    ])
    styler = styler.set_properties(**{'background-color': cell_props[0][1], 'color': cell_props[1][1]})
    return styler

# (Restante das funções de lógica sem alterações)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('plant_data.csv')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except FileNotFoundError:
        st.error("Arquivo 'plant_data.csv' não encontrado. Execute 'gerador_dados_planta.py' primeiro.")
        return None

def load_or_create_service_orders():
    if not os.path.exists(OS_FILE_PATH):
        df_os = pd.DataFrame(columns=['os_id', 'asset_id', 'asset_type', 'creation_date', 'reason', 'priority', 'status', 'completion_date'])
        df_os.to_csv(OS_FILE_PATH, index=False)
        return df_os
    df_os = pd.read_csv(OS_FILE_PATH)
    df_os['creation_date'] = pd.to_datetime(df_os['creation_date'])
    df_os['completion_date'] = pd.to_datetime(df_os['completion_date'], errors='coerce')
    return df_os

def save_service_orders(df_os):
    df_os.to_csv(OS_FILE_PATH, index=False)

def apply_alert_rules(df):
    df_alerts = df.copy()
    df_alerts['status'] = 'Normal'
    df_alerts['status_reason'] = ''
    for asset_type, profile in ASSET_PROFILES.items():
        for param, rules in profile['params'].items():
            if param in df_alerts.columns:
                crit_high = rules['op_max'] * rules['crit_factor']
                warn_high = rules['op_max'] * rules['warn_factor']
                crit_low = rules['op_min'] / rules['crit_factor']
                warn_low = rules['op_min'] / rules['warn_factor']
                is_type = (df_alerts['asset_type'] == asset_type)
                df_alerts.loc[is_type & (df_alerts[param] > crit_high), ['status', 'status_reason']] = ['Crítico', f'{param.title()} Alta']
                df_alerts.loc[is_type & (df_alerts[param] < crit_low), ['status', 'status_reason']] = ['Crítico', f'{param.title()} Baixa']
                df_alerts.loc[is_type & (df_alerts[param] > warn_high) & (df_alerts[param] <= crit_high), ['status', 'status_reason']] = ['Atenção', f'{param.title()} Alta']
                df_alerts.loc[is_type & (df_alerts[param] < warn_low) & (df_alerts[param] >= crit_low), ['status', 'status_reason']] = ['Atenção', f'{param.title()} Baixa']
    return df_alerts

def process_alerts_and_generate_os(df_alerts, df_os):
    critical_problems = df_alerts[df_alerts['status'] == 'Crítico'][['asset_id', 'asset_type', 'status_reason']].drop_duplicates()
    new_os_created = False
    for _, problem in critical_problems.iterrows():
        has_active_os = not df_os[(df_os['asset_id'] == problem['asset_id']) & (df_os['reason'] == problem['status_reason']) & (df_os['status'].isin(['Aberta', 'Em Andamento']))].empty
        if not has_active_os:
            new_os_id = f"OS-{int(datetime.now().timestamp())}-{np.random.randint(100, 999)}"
            new_os = pd.DataFrame([{'os_id': new_os_id, 'asset_id': problem['asset_id'], 'asset_type': problem['asset_type'], 'creation_date': datetime.now(), 'reason': problem['status_reason'], 'priority': 'Crítica', 'status': 'Aberta', 'completion_date': pd.NaT}])
            df_os = pd.concat([df_os, new_os], ignore_index=True)
            new_os_created = True
    if new_os_created:
        save_service_orders(df_os)
        st.toast("Novas Ordens de Serviço foram geradas!", icon="✅")
    return df_os


# --- Carregamento e Processamento Inicial ---
df = load_data()
if df is None: st.stop()
df_analyzed = apply_alert_rules(df)
df_os = load_or_create_service_orders()
df_os = process_alerts_and_generate_os(df_analyzed, df_os)


# --- INÍCIO DA INTERFACE DO USUÁRIO ---
# --- Título e Botão de Tema ---
title_col, button_col = st.columns([0.95, 0.05])
with title_col:
    st.title("🏭 Gestão de Ativos e Manutenção")
with button_col:
    theme_icon = "☀️" if st.session_state.theme == "dark" else "🌙"
    if st.button(theme_icon, key="theme_toggle", help="Alternar tema claro/escuro"):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.rerun()

# --- Abas de Navegação ---
tab1, tab2, tab3, tab4 = st.tabs(["Visão Geral da Planta", "Mapa da Planta", "Análise de Ativo", "Gestão de Ordens de Serviço"])

with tab1:
    st.header("Visão Geral da Planta (Últimas 24 Horas)")
    max_timestamp = df_analyzed['timestamp'].max()
    cutoff_24h = max_timestamp - pd.Timedelta(hours=24)
    df_last_24h = df_analyzed[df_analyzed['timestamp'] >= cutoff_24h]
    total_assets = df['asset_id'].nunique()
    assets_with_alerts_24h = df_last_24h[df_last_24h['status'] != 'Normal']['asset_id'].nunique()
    os_abertas_count = df_os[df_os['status'] == 'Aberta'].shape[0]
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Ativos", f"{total_assets}")
    col2.metric("Ativos com Alertas (24h)", f"{assets_with_alerts_24h}")
    col3.metric("Ordens de Serviço Abertas", f"{os_abertas_count}")
    
    st.subheader("Status dos Ativos (24h)")
    asset_status_summary = df_last_24h.groupby('asset_id').agg(
        asset_type=('asset_type', 'first'),
        location=('location', 'first'),
        status=('status', lambda x: 'Crítico' if 'Crítico' in x.values else ('Atenção' if 'Atenção' in x.values else 'Normal'))
    ).reset_index()
    
    def style_alert_rows(row):
        if row.status == 'Crítico': return ['background-color: #8B0000; color: white'] * len(row)
        if row.status == 'Atenção': return ['background-color: #FFD700; color: #31333F'] * len(row)
        return [''] * len(row)
        
    themed_styler = style_dataframe(asset_status_summary, st.session_state.theme)
    st.dataframe(themed_styler.apply(style_alert_rows, axis=1), use_container_width=True)

with tab2:
    # (Código da Tab2 permanece o mesmo)
    st.header("🗺️ Mapa da Planta")
    asset_locations = df_analyzed[['asset_id', 'latitude', 'longitude']].drop_duplicates().set_index('asset_id')
    asset_status_summary_map = df_analyzed[df_analyzed['timestamp'] >= (df_analyzed['timestamp'].max() - pd.Timedelta(hours=1))].groupby('asset_id').agg(
        status=('status', lambda x: 'Crítico' if 'Crítico' in x.values else ('Atenção' if 'Atenção' in x.values else 'Normal'))
    ).reset_index().set_index('asset_id')
    map_data = asset_locations.join(asset_status_summary_map).reset_index()
    color_map = {'Normal': '#008000', 'Atenção': '#FFA500', 'Crítico': '#FF0000'}
    map_data['color'] = map_data['status'].map(color_map)
    map_data.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True)
    st.map(map_data, color='color', size=20)
    st.write("### Legenda")
    st.markdown("""
    - <span style="color:#008000">**Verde:**</span> Ativo em status Normal
    - <span style="color:#FFA500">**Laranja:**</span> Ativo em status de Atenção
    - <span style="color:#FF0000">**Vermelho:**</span> Ativo em status Crítico
    """, unsafe_allow_html=True)


with tab3:
    st.header("Análise Detalhada por Ativo")
    selected_asset_id = st.selectbox('Selecione um Ativo:', options=df['asset_id'].unique())
    if selected_asset_id:
        df_asset_detail = df_analyzed[df_analyzed['asset_id'] == selected_asset_id]
        st.subheader(f"Dados do Ativo: {selected_asset_id}")
        sensor_cols_detail = [c for c in df_asset_detail.select_dtypes(include=np.number).columns if c not in ['latitude', 'longitude']]
        chart_theme = "plotly_dark" if st.session_state.theme == "dark" else "plotly_white"
        for sensor in sensor_cols_detail:
            fig = px.line(df_asset_detail, x='timestamp', y=sensor, 
                          title=f'Leituras de {sensor.replace("_", " ").title()}',
                          template=chart_theme)
            alerts_warn = df_asset_detail[df_asset_detail['status'] == 'Atenção']
            alerts_crit = df_asset_detail[df_asset_detail['status'] == 'Crítico']
            if not alerts_warn.empty: fig.add_scatter(x=alerts_warn['timestamp'], y=alerts_warn[sensor], mode='markers', name='Atenção', marker=dict(color='orange', size=8, symbol='triangle-up'))
            if not alerts_crit.empty: fig.add_scatter(x=alerts_crit['timestamp'], y=alerts_crit[sensor], mode='markers', name='Crítico', marker=dict(color='red', size=8, symbol='x'))
            st.plotly_chart(fig, use_container_width=True, key=f"chart_{sensor}_{selected_asset_id}_{st.session_state.theme}")

with tab4:
    st.header("⚙️ Gestão de Ordens de Serviço")
    status_filter = st.multiselect('Filtrar por Status:', options=df_os['status'].unique(), default=df_os['status'].unique())
    priority_filter = st.multiselect('Filtrar por Prioridade:', options=df_os['priority'].unique(), default=df_os['priority'].unique())
    df_os_filtered = df_os[df_os['status'].isin(status_filter) & df_os['priority'].isin(priority_filter)]
    
    themed_os_styler = style_dataframe(df_os_filtered, st.session_state.theme)
    st.dataframe(themed_os_styler, use_container_width=True)
    
    st.subheader("Atualizar uma Ordem de Serviço")
    os_to_update_options = df_os[df_os['status'] != 'Concluída']['os_id'].tolist()
    if not os_to_update_options:
        st.info("Não há ordens de serviço para atualizar.")
    else:
        selected_os_id = st.selectbox("Selecione a OS para atualizar:", options=os_to_update_options)
        new_status = st.selectbox("Selecione o novo status:", options=['Em Andamento', 'Concluída'])
        if st.button("Atualizar Status da OS"):
            os_index = df_os.index[df_os['os_id'] == selected_os_id].tolist()
            if os_index:
                idx = os_index[0]
                df_os.loc[idx, 'status'] = new_status
                if new_status == 'Concluída':
                    df_os.loc[idx, 'completion_date'] = datetime.now()
                save_service_orders(df_os)
                st.success(f"Ordem de Serviço {selected_os_id} atualizada para '{new_status}'!")
                st.rerun()