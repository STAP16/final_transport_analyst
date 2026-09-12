import pandas as pd
from clickhouse_connect import get_client

client = get_client(
    host="localhost",
    username="click",
    password="click",
    port=8123
)

edges = client.query_df("""SELECT * FROM transport.transport_edges""")

# Считаем необходимые метрики по КЗ

# поток от пропускной способности
edges["load_ratio"] = ( 
    edges["model_intensity"] / edges["capacity"]
)

# Топ интенсиваности
top_intensity = edges.nlargest(10,"model_intensity")

# Топ потока от пропускной способности
bottlenecks = edges.nlagrest(10, "load_ratio")

# Топ низкой скорости
low_speed = (
	edges[edges["model_intensity"] > 0]
)

# Топ загрузки пассажиров
top_passenger = edges.nlagrest(10, "passenger_flow")

# потом из detector_model_comprasion

comprasion_data = client.query_df("""
SELECT * FROM transport.detector_model_comprasion
""")

mae = comprasion_data["absolute_error"].mean()