import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA
from utilities import (
    apply_theme, load_assets,
    check_authentication, has_page_access, render_sidebar, ASSET_PROFILES, engine
)
import warnings

# Ignora avisos comuns do ARIMA para uma interface mais limpa
warnings.filterwarnings("ignore")

# --- Autenticação e Configuração ---
check_authentication()
render_sidebar()
has_page_access("11_Failure_Prediction") # Ajuste o nome se o seu for diferente
apply_theme()

st.title("🤖 Previsão de Falhas (Análise Preditiva)")
st.write("Esta página varre todos os ativos e sensores, usando um modelo de Machine Learning (ARIMA) para prever tendências futuras e alertar sobre possíveis falhas antes que elas aconteçam.")

# --- Lógica de Previsão ---

@st.cache_data
def get_sensor_history(asset_id, sensor):
    """Carrega o histórico de um sensor específico do banco de dados."""
    query = f"SELECT timestamp, {sensor} FROM sensor_data WHERE asset_id = ? ORDER BY timestamp DESC LIMIT 200"
    df = pd.read_sql(query, engine, params=(asset_id,), index_col='timestamp', parse_dates=['timestamp'])
    return df.iloc[::-1]

@st.cache_data
def get_forecast(series, forecast_hours, order=(5,1,0)):
    """Treina um modelo ARIMA e retorna a previsão."""
    try:
        model = ARIMA(series, order=order, enforce_stationarity=False, enforce_invertibility=False)
        model_fit = model.fit()
        return model_fit.forecast(steps=forecast_hours)
    except Exception as e:
        return None

# --- Execução da Análise ---

df_assets = load_assets()
at_risk_assets = []

if df_assets.empty:
    st.warning("Nenhum ativo cadastrado. Por favor, cadastre ativos na página 'Gestão de Ativos'.")
else:
    progress_bar = st.progress(0, text="Iniciando varredura dos ativos...")

    # --- CORREÇÃO: Cálculo correto do total de sensores a verificar ---
    total_sensors_to_check = sum(
        len(ASSET_PROFILES.get(asset['asset_type'], {}).get('params', []))
        for _, asset in df_assets.iterrows()
    )
    
    checked_sensors = 0
    if total_sensors_to_check == 0:
        st.warning("Nenhum perfil de sensor corresponde aos ativos cadastrados. Verifique os 'asset_type' em 'Gestão de Ativos'.")
        st.stop()

    for index, asset in df_assets.iterrows():
        asset_id = asset['asset_id']
        asset_type = asset['asset_type']
        
        profile = ASSET_PROFILES.get(asset_type)
        if not profile:
            continue

        for sensor, config in profile['params'].items():
            checked_sensors += 1
            progress_text = f"Analisando {asset_id} -> Sensor: {sensor}..."
            
            # --- CORREÇÃO: Trava de segurança para o valor do progresso ---
            progress_value = min(1.0, checked_sensors / total_sensors_to_check)
            progress_bar.progress(progress_value, text=progress_text)

            history = get_sensor_history(asset_id, sensor)
            if not history.empty and len(history) > 20: # Garante dados suficientes para o modelo
                forecast_hours = 24
                forecast = get_forecast(history[sensor], forecast_hours)
                
                if forecast is not None:
                    critical_threshold = config['op_max'] * config['crit_factor']
                    
                    if (forecast > critical_threshold).any():
                        time_to_failure = forecast[forecast > critical_threshold].index[0]
                        hours_to_failure = int((time_to_failure - history.index[-1]).total_seconds() / 3600)
                        at_risk_assets.append({
                            "asset_id": asset_id, "asset_type": asset_type, "sensor": sensor,
                            "history": history, "forecast": forecast, "threshold": critical_threshold,
                            "hours_to_failure": hours_to_failure
                        })
    
    progress_bar.progress(1.0, text="Análise concluída!")

# --- Exibição dos Resultados ---
st.divider()

if not at_risk_assets:
    st.success("✅ Nenhuma anomalia prevista. Todos os ativos estão operando dentro das tendências seguras.")
else:
    st.error(f"🚨 ALERTA: {len(at_risk_assets)} evento(s) de falha previstos!")
    
    sorted_assets = sorted(at_risk_assets, key=lambda x: x['hours_to_failure'])

    for asset in sorted_assets:
        with st.expander(f"**{asset['asset_id']} ({asset['asset_type']})** - Falha prevista em **~{asset['hours_to_failure']} horas** no sensor **{asset['sensor']}**"):
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=asset['history'].index, y=asset['history'][asset['sensor']], mode='lines', name='Histórico'))
            fig.add_trace(go.Scatter(x=asset['forecast'].index, y=asset['forecast'], mode='lines', name='Previsão (ARIMA)', line={'dash': 'dash'}))
            fig.add_hline(y=asset['threshold'], line_width=2, line_dash="dot", line_color="red", name=f"Limite Crítico ({asset['threshold']:.2f})")
            
            fig.update_layout(
                title=f"Previsão para {asset['sensor']} no ativo {asset['asset_id']}",
                xaxis_title="Data/Hora",
                yaxis_title=f"Leitura do Sensor ({asset['sensor']})",
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)