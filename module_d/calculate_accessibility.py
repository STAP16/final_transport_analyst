import pandas as pd
from clickhouse_connect import get_client

client = get_client(
    host="localhost",
    username="click",
    password="click",
    port=8123
)

df = pd.read_excel(r'module_d\cost_matrix_ttc.xlsx', sheet_name="Данные Матрицы")

# melt - превращаем в обычную таблицу
costs = df.melt(
	id_vars=["Районы"],
	var_name="destination",
	value_name="travel_time"
)

costs["zone_id"] = (
	costs["Районы"].str.split(".").str[0].astype(int)
)

costs["destination_id"] = (
	costs["destination"].str.split(".").str[0].astype(int)
)

# Дропаем пустые значение
costs = costs.dropna(subset=["zone_id", "destination_id", "travel_time"])

# в РИТМ значение 999999 означаает "путь не найден"
# оставить все реальные значения и выбросить 999999.
costs = costs[costs["travel_time"] < 999999] 

# mean — это уже наше выбранное определение показателя доступности
# Мы основе матрицы определили доступность как среднее время достижения остальных районов.
accessibility = (
	costs.groupby("zone_id", as_index=False)
	.agg(
		accessibility=("travel_time", "mean")
	)
)

# чем меньше среднее время достижения других транспортных районов, тем выше транспортная доступность района.

print(accessibility)

client.insert_df("transport.accessibility_results", accessibility)

print("Вставлено: ", len(accessibility))