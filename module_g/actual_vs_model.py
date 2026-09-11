# pessenger_flow
# model_intensity
# model_speed

import pandas as pd
import numpy as np
from clickhouse_connect import get_client
client = get_client(host="localhost", username="click", password="click", port=8123)

model = pd.read_excel(r"module_g\Отрезки.xlsx", skiprows=2)
print(model.columns.tolist())

model = model[[
    "ID отрезка",
    "Нагрузка [ТС] ИТ(ПА)",
    "vАкт-СисТрИТ(L,ПА)",
    "Нагрузка [Чел]-ОТ(ПА)"
]]


model.columns = [
    "edge_id",
    "model_intensity",
    "model_speed",
    "passenger_flow"
]

mapping = client.query_df("""SELECT * FROM transport.detector_edge_mapping""")

actual = client.query_df("""
    SELECT
        detector_id,
        avg(avg_intensity) AS actual_intensity
    FROM transport.detectors_aggregates
    WHERE aggregate_type = 'date'
    GROUP BY detector_id
""")

actual = actual.merge(
	mapping,
	on="detector_id",
	how="inner"
)

comprasion = actual.merge(
	model,
	on="edge_id",
	how="inner"
)

print(comprasion)
# Тут заканчивается comprasion по репрезентативному фактическое значение на детектор. Например среднее по всем суточным агрегатам:

# расчет метрик качества модели

comprasion["absolute_error"] = (
	comprasion["model_intensity"] - comprasion["actual_intensity"]
).abs()

comprasion["percentage_error"] = (
	comprasion["absolute_error"] / comprasion["actual_intensity"] * 100
)

mae = comprasion["absolute_error"].mean()
rmse = np.sqrt(
    (
        (
            comprasion["model_intensity"]
            - comprasion["actual_intensity"]
        ) ** 2
    ).mean()
)

mape = comprasion["percentage_error"].mean()

correlation = comprasion[
    ["actual_intensity", "model_intensity"]
].corr().iloc[0, 1]
worst = comprasion.sort_values(
	"absolute_error",
	ascending=False
).head(10)

cols = [
	"detector_id",
	"edge_id",
	"actual_intensity",
	"model_intensity",
	"model_speed", 
	"passenger_flow",
	"distance_m",
	"absolute_error",
	"percentage_error"
]

client.insert_df(table="transport.detector_model_comprasion", df=comprasion[cols], column_names=cols)

print('MAE: ', mae)
print("RMSE: ", rmse)
print("MAPE: ", mape)
print("CORRELATION: ", correlation)
print("WORST:\n", worst)