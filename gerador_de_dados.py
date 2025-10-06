import pandas as pd
import numpy as np
import random
import uuid
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
from utilities import initialize_database, ASSET_PROFILES, engine, save_assets

print("Iniciando a geração de dados...")

# Limpa todas as tabelas transacionais e recria a estrutura do DB
initialize_database(clear_all=True)

tipos_de_equipamentos = [
    "Torno CNC", "Fresadora", "Compressor de Ar Industrial", "Prensa Hidráulica",
    "Caldeira a Vapor", "Gerador de Energia a Diesel", "Robô de Soldagem",
    "Esteira Transportadora", "Empilhadeira", "Trocador de Calor", "Bomba Centrífuga",
    "Forno de Indução", "Misturador Industrial", "Reator Químico",
    "Máquina de Injeção de Plástico", "Sistema de Filtração Industrial",
    "Célula de Carga", "Ponte Rolante", "Extrusora", "CLP",
    "Máquina de Corte a Laser", "Dobradeira de Chapas", "Torre de Resfriamento",
    "Moinho de Bolas", "Secador Industrial", "Guilhotina Industrial",
    "Autoclave Industrial", "Sistema de Visão Computacional", "Chiller Industrial",
    "Silo de Armazenamento"
]

total_ativos = 150
ativos_por_tipo = total_ativos // len(tipos_de_equipamentos)
lista_de_ativos = []

print(f"Gerando {total_ativos} ativos...")
for tipo in tipos_de_equipamentos:
    for i in range(1, ativos_por_tipo + 1):
        tipo_id = tipo.replace(' ', '_').upper()
        asset_id = f"{tipo_id}-{str(i).zfill(3)}"
        location = f"Setor {random.choice(['A','B','C','D','E'])}-Linha {random.randint(1, 10)}"
        install_date = (datetime.now() - timedelta(days=random.randint(30, 365*5))).strftime('%Y-%m-%d')
        lista_de_ativos.append({'asset_id': asset_id, 'asset_type': tipo, 'location': location, 'description': f"{tipo} modelo #{i}", 'install_date': install_date})

df_assets = pd.DataFrame(lista_de_ativos)
save_assets(df_assets)
print(f"{len(df_assets)} ativos criados e salvos.")

NUM_PONTOS = 1440
FREQ = '1min'
all_sensor_data = []
print("Gerando dados de sensores...")

for index, asset in df_assets.iterrows():
    asset_id = asset['asset_id']
    asset_type = asset['asset_type']
    if asset_type in ASSET_PROFILES:
        profile = ASSET_PROFILES[asset_type]
        timestamps = pd.date_range(end=pd.Timestamp.now(), periods=NUM_PONTOS, freq=FREQ)
        sensor_data_dict = {
            'timestamp': timestamps, 'asset_id': asset_id, 'asset_type': asset_type,
            'location': asset['location'], 'latitude': -18.420 + random.uniform(-0.008, 0.008),
            'longitude': -49.225 + random.uniform(-0.008, 0.008)
        }
        for param, config in profile['params'].items():
            dados_normais = config['mean'] + config['std'] * np.random.randn(NUM_PONTOS)
            sensor_data_dict[param] = np.clip(dados_normais, config['op_min'] * 0.9, config['op_max'] * 1.1)
        
        df_sensor_asset = pd.DataFrame(sensor_data_dict)
        
        if random.random() < 0.20:
            param_to_affect = random.choice(list(profile['params'].keys()))
            start_index = random.randint(0, NUM_PONTOS - 60)
            end_index = start_index + random.randint(10, 20)
            anomalous_value = profile['params'][param_to_affect]['op_max'] * profile['params'][param_to_affect].get('crit_factor', 1.5)
            df_sensor_asset.loc[start_index:end_index, param_to_affect] = anomalous_value + np.random.randn()
        
        all_sensor_data.append(df_sensor_asset)

if all_sensor_data:
    df_final_sensores = pd.concat(all_sensor_data, ignore_index=True)
    try:
        df_final_sensores.to_sql('sensor_data', engine, if_exists='append', index=False, chunksize=10000)
        print(f"Dados de sensores salvos com sucesso.")
    except Exception as e:
        print(f"Ocorreu um erro ao salvar os dados de sensores no banco de dados: {e}")