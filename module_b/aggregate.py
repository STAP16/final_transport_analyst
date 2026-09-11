import geopandas as gpd

zones = gpd.read_file("module_b\Районы.geojson")
objects = gpd.read_file("module_b\Учебные объекты.geojson")

# Приводим объекты к той же системе координат

objects = objects.to_crs(zones.crs)

# Привязываем каждый объект к району, внутри которого он находится

joined = gpd.sjoin(
	objects,
	zones[["no", "geometry"]], # Связываем Номер объекта, с геометрией зоны
	how="left",
	predicate="within"
)

# Агрегируем по районам
result = (
	joined.groupby("no", as_index=False)
	.agg(
		population=("population", "sum"),
		workplaces=("workplaces", "sum")
	)
)

print(result)

result.to_excel(
	"Агрегация по районам.xlsx",
	index=False
)