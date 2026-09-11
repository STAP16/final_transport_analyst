from clickhouse_connect import get_client

client = get_client(host="localhost", username="click", password="click", port=8123)

db = "transport"

def create_table_transport_zones():

	name = "transport_zones "

	# Таблица транспортных зон
	# Айди, название, кол-во людей, кол-во рабочих мест, геомитрия зоны

	client.command(f"""
	CREATE TABLE IF NOT EXISTS {db}.{name}
	(
		zone_id UInt64,
		name String,
		population UInt64,
		workplaces UInt64,
		geometry String
	)
	ENGINE = MergeTree
	ORDER BY zone_id
	"""
	)


def create_table_transport_edges():

	name = "transport_edges "

	# Таблица трансопртных узлов (участки дороги)
	# айди, длина, интенсивность,полученная с модели. Скорость с модели, пассажиропоток на участке транспортной сети (Нагрузка [Чел]-ОТ(ПА) из РИТМ), вместимость машин (Максимальная пропускная способность из РИТМ), геометрия 

	client.command(f"""
	CREATE TABLE IF NOT EXISTS {db}.{name}
	(
		edge_id UInt64,
		length_m Float64,
		model_intensity Float64,
		model_speed Float64,
		passenger_flow Float64,
		capacity Float64,
		geometry String
	)
	ENGINE = MergeTree
	ORDER BY edge_id
	"""
	)


def create_table_detectors():

	name = "detectors"


	# Таблица детекторов (Скорее всего выдадут)
	# Айди, имя, longtude (Долгота), latude(Широта)

	client.command(f"""
	CREATE TABLE IF NOT EXISTS {db}.{name}
	(
		detector_id UInt64,
		name String,
		lon Float64,
		lat Float64
	)
	ENGINE = MergeTree
	ORDER BY detector_id
	"""
	)


def create_table_detectors_measurements():

	name = "detectors_measurements"

	# Таблица данных с декторов
	# Айди, время детекта, интенсивность, скорость


	client.command(f"""
	CREATE TABLE IF NOT EXISTS {db}.{name}
	(
		detector_id UInt64,
		measured_at DateTime64(3), 
		intensity Float64,
		speed Float64
	)
	ENGINE = MergeTree
	ORDER BY detector_id
	"""
	)


def create_table_detectors_aggregates():

	name = "detectors_aggregates"

	# Агрегированные детекторы
	# Тип агрегации: day / hourly / weekday / monthly
	# С какого по какой (YYYY-MM-DD)
	# Средняя интенсивность
	# Средняя скорость

	client.command(f"""
	CREATE TABLE IF NOT EXISTS {db}.{name}
	(
		detector_id String,
		aggregate_type String,
		period_value String,
		avg_intensity Float64,
		avg_speed Float64,
		irregularity Nullable(Float64)
	)
	ENGINE = MergeTree
	ORDER BY (detector_id, aggregate_type, period_value)
	"""
	)


def create_table_detector_edge_mapping():

	name = "detector_edge_mapping"

	# Маппер по декторам и узлам
	# Айди детектора, айди узла, дистанция в метрах.

	client.command(f"""
	CREATE TABLE IF NOT EXISTS {db}.{name}
	(
		detector_id String,
		edge_id UInt64,
		distance_m Float64
	)
	ENGINE = MergeTree
	ORDER BY (detector_id, edge_id)
	"""
	)

def create_table_detector_model_comprasion():
	name = "detector_model_comprasion"

	# Склеивание фактических данных и данных с модели
	# Айди детектора, Айди узла, реальная интенсивность, интенсивность модели, скорость модели, вместимость человек, дистанция, абсолютная ошибка, средне квадратичная ошибка

	client.command(f"""
	CREATE TABLE IF NOT EXISTS {db}.{name}
	(
		detector_id String,
		edge_id UInt64,
		actual_intensity Float64,
		model_intensity Float64,
		model_speed Float64, 
		passenger_flow Float64,
		distance_m Float64,
		absolute_error Float64,
		percentage_error Nullable(Float64)
	)
	ENGINE = MergeTree
	ORDER BY (detector_id, edge_id)
	"""
	)

def init_db():
	client.command(f"DROP DATABASE IF EXISTS {db}")
	client.command(f"CREATE DATABASE IF NOT EXISTS {db}")

	create_table_detector_edge_mapping()
	create_table_detector_model_comprasion()
	create_table_detectors_aggregates()
	create_table_transport_edges()
	create_table_transport_zones()
	create_table_detectors_measurements()
	create_table_detectors()

	print(f"database: {db}, has been created")

init_db()