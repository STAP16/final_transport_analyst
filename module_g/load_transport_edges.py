import pandas as pd
import numpy as np
from db.connection import engine

model = pd.read_excel(r"module_g\Отрезки.xlsx", skiprows=2) # Это уже файл с расчетными данными
print(model.columns.tolist())

# Максимальная пропускная способность, длина и геометрия должны совпасть именно с названиями в твоей конкретной выгрузке RITM.

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

edges["load_ratio"] = (
    edges["model_intensity"] / edges["capacity"]
)

edges["length_m"] = edges["length_m"] * 1000

edges.to_sql(
    "transport_edges",
    engine,
    if_exists="append",
    index=False
)

print("Загружено: ", len(edges))