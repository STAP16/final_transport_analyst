import pandas as pd
import geopandas as gpd

from clickhouse_connect import get_client

client = get_client(host="localhost", username="click", password="click", port=8123)

db = "transport"


df = pd.read_csv(r"module_v\detectors.csv")
edges = gpd.read_file("module_v\Отрезки.geojson")

# У дектеров забираем нужные поля по которым будем маппить
detectors = df[["detector_id", "lon", "lat"]].drop_duplicates()

# Превращаем обычный DataFrame в пространственный
detectors = gpd.GeoDataFrame(
	detectors,
	geometry=gpd.points_from_xy(detectors.lon, detectors.lat), # Создаем из координат геометрию
	crs="EPSG:4326" #В такой геометрической системе расчета работает GeoPandas
)

# Приводим детекторы к той же системе координат что и отрезки
detectors = detectors.to_crs(edges.crs)

# Маппим именно с вопросом: "Какой edge находится ближе к точке detector"
mapping = gpd.sjoin_nearest(
	detectors,
	edges[["no", "geometry"]],
	how="left",
	distance_col="distance_m"
)

# Убираем дубликаты
mapping = (
	mapping.sort_values("distance_m")
	.drop_duplicates(subset="detector_id", keep="first")
)
# Оставляем только те поля, которые есть в БД
mapping = mapping[["detector_id", "no", "distance_m"]]
mapping.columns = ["detector_id", "edge_id", "distance_m"]

# Вставка
client.insert_df(
    f"{db}.detector_edge_mapping",
    mapping
)

print("Данные успешно вставлены: ", len(mapping))