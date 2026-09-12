import pandas as pd
from clickhouse_connect import get_client

client = get_client(
    host="localhost",
    username="click",
    password="click",
    port=8123
)


def prepare_matrix(path):
	df = pd.read_excel(
		path,
		sheet_name="Данные Матрицы"
	)

	matrix = df.melt(
		id_vars=["Районы"],
		var_name="destination",
		value_name="flow"
	)

	matrix["origin_id"] = (
		matrix["Районы"]
		.str.split(".").str[0]
		.astype(int)
	)

	matrix["destination_id"] = (
		matrix["destination"]
		.str.split(".").str[0]
		.astype(int)
	)

	return matrix[["origin_id", "destination_id", "flow"]]

private = prepare_matrix(r"module_d\od_private.xlsx")

public = prepare_matrix(r"module_d\od_public.xlsx")

od = private.merge(
	public,
	on=["origin_id", "destination_id"],
	suffixes=("_private", "_public")
)

od["flow"] = (
	od["flow_private"] + od["flow_public"]
)

# Исключаем внутрирайонные перемещения
od = od[
    od["origin_id"] != od["destination_id"]
]

# И нулевые пары
od = od[
    od["flow"] > 0
]

od = od[
    ["origin_id", "destination_id", "flow"]
]

print(od.head())

client.insert_df(
    "transport.od_matrix",
    od
)

print("Вставлено в таблицу: ", len(od))