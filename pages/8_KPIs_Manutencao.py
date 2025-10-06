import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utilities import (
    apply_theme, load_service_orders,
    check_authentication, has_page_access, render_sidebar
)
from datetime import datetime

# --- Autenticação e Configuração da Página ---
check_authentication()
render_sidebar()
has_page_access("8_KPIs_Manutencao")
apply_theme()

st.title("📈 Dashboard de KPIs de Manutenção")

df_os = load_service_orders()

# --- Filtros Principais da Página ---
st.sidebar.header("Filtros de KPI")
# Filtro de data na barra lateral para aplicar a toda a página
min_date = df_os['creation_date'].min().date()
max_date = df_os['creation_date'].max().date()

date_range = st.sidebar.date_input(
    "Selecione o Período de Análise",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Garante que temos um range de datas válido
if len(date_range) != 2:
    st.stop()

start_date, end_date = date_range
# Converte as datas para datetime para filtrar corretamente
df_os_filtered = df_os[
    (df_os['creation_date'].dt.date >= start_date) & 
    (df_os['creation_date'].dt.date <= end_date)
]

# Dataframe base para cálculos: OS de falha que foram concluídas no período
df_failures = df_os_filtered[
    (df_os_filtered['status'] == 'Concluída') &
    (df_os_filtered['class'].isin(['Preditiva', 'Corretiva'])) &
    (pd.notna(df_os_filtered['completion_date']))
].copy()

st.header("Análise Geral do Período")

if df_failures.empty:
    st.warning("Não há dados de ordens de serviço de falha concluídas no período selecionado para calcular os KPIs.")
else:
    # --- 1. KPIs Gerais (MTTR, Custo Total) ---
    df_failures['duration_hours'] = (df_failures['completion_date'] - df_failures['creation_date']).dt.total_seconds() / 3600
    overall_mttr = df_failures['duration_hours'].mean()
    total_failures = len(df_failures)
    total_cost = df_failures['actual_cost'].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Falhas Analisadas", f"{total_failures}")
    col2.metric("MTTR Geral (Horas)", f"{overall_mttr:.2f}")
    col3.metric("Custo Total de Reparos", f"R$ {total_cost:,.2f}")

    st.divider()
    st.header("Análise de Causa Raiz (Princípio de Pareto)")

    # Filtra causas não definidas
    rca_df = df_failures[df_failures['root_cause'].notna() & (df_failures['root_cause'] != 'Não Definida')]

    if rca_df.empty:
        st.info("Nenhuma causa raiz foi registrada para as falhas no período selecionado.")
    else:
        cause_counts = rca_df['root_cause'].value_counts().reset_index()
        cause_counts.columns = ['Causa Raiz', 'Frequência']
        
        # Calcula a porcentagem acumulada para o gráfico de Pareto
        cause_counts = cause_counts.sort_values(by='Frequência', ascending=False)
        cause_counts['Porcentagem Acumulada'] = (cause_counts['Frequência'].cumsum() / cause_counts['Frequência'].sum()) * 100

        fig_pareto = go.Figure()
        # Barra para a frequência
        fig_pareto.add_trace(go.Bar(
            x=cause_counts['Causa Raiz'],
            y=cause_counts['Frequência'],
            name='Frequência',
            marker_color='royalblue'
        ))
        # Linha para a porcentagem acumulada
        fig_pareto.add_trace(go.Scatter(
            x=cause_counts['Causa Raiz'],
            y=cause_counts['Porcentagem Acumulada'],
            name='Acumulado %',
            yaxis='y2',
            line=dict(color='red', width=2)
        ))
        fig_pareto.update_layout(
            title="Gráfico de Pareto - Causas Raiz de Falhas",
            xaxis_title="Causa Raiz",
            yaxis_title="Número de Ocorrências",
            yaxis2=dict(
                title="Porcentagem Acumulada (%)",
                overlaying="y",
                side="right",
                range=[0, 105]
            ),
            template="plotly_dark",
            legend=dict(yanchor="top", y=0.9, xanchor="left", x=0.8)
        )
        st.plotly_chart(fig_pareto, use_container_width=True)
        st.info("O Gráfico de Pareto ajuda a identificar as 'poucas causas vitais' que são responsáveis pela maioria das falhas (o princípio 80/20). Foque nas primeiras barras para ter o maior impacto nas melhorias.")

    # --- 2. Análise de Tendências Temporais (NOVOS GRÁFICOS) ---
    st.divider()
    st.header("Tendências Temporais")
    
    time_agg_option = st.selectbox(
        "Agrupar dados por:",
        options=['Diário', 'Semanal', 'Mensal', 'Trimestral', 'Anual']
    )
    time_mapping = {'Diário': 'D', 'Semanal': 'W', 'Mensal': 'M', 'Trimestral': 'Q', 'Anual': 'Y'}
    
    # Prepara dados para os gráficos de tendência
    df_trends = df_failures.set_index('completion_date')
    
    # Gráfico 1: Custo ao longo do tempo
    costs_over_time = df_trends['actual_cost'].resample(time_mapping[time_agg_option]).sum()
    fig_cost_trend = px.line(costs_over_time, x=costs_over_time.index, y='actual_cost',
                             title=f"Custo de Manutenção ({time_agg_option})",
                             labels={'completion_date': 'Período', 'actual_cost': 'Custo Total (R$)'},
                             template='plotly_dark', markers=True)
    st.plotly_chart(fig_cost_trend, use_container_width=True)

    # Gráfico 2: Número de falhas ao longo do tempo
    failures_over_time = df_trends['os_id'].resample(time_mapping[time_agg_option]).count()
    fig_failures_trend = px.bar(failures_over_time, x=failures_over_time.index, y='os_id',
                                title=f"Número de Falhas ({time_agg_option})",
                                labels={'completion_date': 'Período', 'os_id': 'Nº de Falhas'},
                                template='plotly_dark')
    st.plotly_chart(fig_failures_trend, use_container_width=True)

    # --- 3. Análise de Composição e Ranking (NOVOS GRÁFICOS) ---
    st.divider()
    st.header("Composição e Ranking")
    
    col_pie, col_top5 = st.columns(2)

    with col_pie:
        # Gráfico 3: Distribuição de OS por Classe
        class_counts = df_os_filtered['class'].value_counts().reset_index()
        fig_pie = px.pie(class_counts, names='class', values='count', 
                         title='Distribuição de OS por Classe',
                         template='plotly_dark')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col_top5:
        # Gráfico 4: Top 5 Ativos com mais Custo
        top_5_cost_assets = df_failures.groupby('asset_id')['actual_cost'].sum().nlargest(5).sort_values()
        fig_top5 = px.bar(top_5_cost_assets, x='actual_cost', y=top_5_cost_assets.index,
                          orientation='h', title='Top 5 Ativos por Custo de Manutenção',
                          labels={'actual_cost': 'Custo Total (R$)', 'y': 'ID do Ativo'},
                          template='plotly_dark')
        st.plotly_chart(fig_top5, use_container_width=True)


    # --- 4. Análise de Confiabilidade (Gráficos Antigos) ---
    st.divider()
    st.header("Análise de Confiabilidade por Tipo de Ativo")
    
    # MTTR por Tipo de Ativo
    mttr_by_asset = df_failures.groupby('asset_type')['duration_hours'].mean().reset_index()
    fig_mttr = px.bar(mttr_by_asset, x='asset_type', y='duration_hours', title='MTTR (Tempo Médio para Reparo) por Tipo de Ativo',
                      labels={'asset_type': 'Tipo de Ativo', 'duration_hours': 'MTTR (Horas)'}, template='plotly_dark')
    st.plotly_chart(fig_mttr, use_container_width=True)

    # MTBF por Tipo de Ativo
    df_failures = df_failures.sort_values(by=['asset_id', 'creation_date'])
    df_failures['previous_completion'] = df_failures.groupby('asset_id')['completion_date'].shift(1)
    df_failures['uptime_hours'] = (df_failures['creation_date'] - df_failures['previous_completion']).dt.total_seconds() / 3600
    df_mtbf = df_failures[df_failures['uptime_hours'] > 0]
    
    if not df_mtbf.empty:
        mtbf_by_asset = df_mtbf.groupby('asset_type')['uptime_hours'].mean().reset_index()
        fig_mtbf = px.bar(mtbf_by_asset, x='asset_type', y='uptime_hours', title='MTBF (Tempo Médio Entre Falhas) por Tipo de Ativo',
                          labels={'asset_type': 'Tipo de Ativo', 'uptime_hours': 'MTBF (Horas)'}, template='plotly_dark')
        st.plotly_chart(fig_mtbf, use_container_width=True)
    else:
        st.info("Não há dados suficientes (falhas consecutivas no mesmo ativo) para calcular o MTBF por tipo de ativo.")