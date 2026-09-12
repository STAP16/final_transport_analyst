import pandas as pd
import numpy as np
from clickhouse_connect import get_client
client = get_client(host="localhost", username="click", password="click", port=8123)

model = pd.read_excel(r"module_g\Отрезки.xlsx", skiprows=2)
print(model.columns.tolist())

edges = model[[
    "ID отрезка",
    "Длина отрезка [км]",
    "Нагрузка [ТС] ИТ(ПА)",
    "vАкт-СисТрИТ(L,ПА)",
    "Нагрузка [Чел]-ОТ(ПА)",
    "Максимальная пропускная способность",
    "Геометрия отрезка"
]].copy()

edges.columns = [
    "edge_id",
    "length_m",
    "model_intensity",
    "model_speed",
    "passenger_flow",
    "capacity",
    "geometry"
]

edges["length_m"] = edges["length_m"] * 1000

client.insert_df(
    "transport.transport_edges",
    edges
)