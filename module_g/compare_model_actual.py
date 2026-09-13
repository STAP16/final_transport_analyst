# pessenger_flow
# model_intensity
# model_speed

import numpy as np
import pandas as pd

from db.connection import engine



edges = pd.read_sql("""SELECT * FROM transport_edges""", engine)

model_for_comparison = edges[[
    "edge_id",
    "model_intensity",
    "model_speed",
    "passenger_flow"
]]

mapping = pd.read_sql("""SELECT * FROM detector_edge_mapping""", engine)

actual = pd.read_sql("""
    SELECT
        detector_id,
        avg(avg_intensity) AS actual_intensity
    FROM detectors_aggregates
    WHERE aggregate_type = 'date'
    GROUP BY detector_id
""", engine)

actual = actual.merge(
	mapping,
	on="detector_id",
	how="inner"
)

comprasion = actual.merge(
	model_for_comparison,
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


comprasion[cols].to_sql(
    "detector_model_comprasion",
    engine,
    if_exists="append",
    index=False
)

# Вставляем метрики в таблицу, которая пригодится для модуля Д

validation_metrics = pd.DataFrame([
    {"metric": "MAE", "value": mae},
    {"metric": "RMSE", "value": rmse},
    {"metric": "MAPE", "value": mape},
    {"metric": "Correlation", "value": correlation},
])

validation_metrics.to_sql("validation_metrics", engine, if_exists="append", index=False)

print("Вставлено метрик качества: ", len(validation_metrics))