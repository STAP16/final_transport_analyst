import psycopg

db = "transport"

def recreate_database():
	admin_conn = psycopg.connect(
		host="127.0.0.1",
		port=5433,
		dbname="postgres", # Подключаемся не к transport
		user="postgres",
		password='postgres'
	)

	admin_conn.autocommit = True
	with admin_conn.cursor() as cursor:
		cursor.execute(f"DROP DATABASE IF EXISTS {db}")
		cursor.execute(f"CREATE DATABASE {db}")

	admin_conn.close()

# Создаем бд

recreate_database()

conn = psycopg.connect(
	host="127.0.0.1",
	port=5433,
	dbname=db,
	user="postgres",
	password="postgres"
)


def create_table_transport_zones():

	name = "transport_zones"

	# Таблица транспортных зон
	# Айди, название, кол-во людей, кол-во рабочих мест, геомитрия зоны

	sql = f"""
	CREATE TABLE IF NOT EXISTS {name}
	(
		zone_id BIGINT PRIMARY KEY,
		name TEXT,
		population BIGINT,
		workplaces BIGINT,
		geometry TEXT
	)
	"""

	with conn.cursor() as cursor:
		cursor.execute(sql)

	conn.commit()


def create_table_transport_edges():

	name = "transport_edges"

	# Таблица трансопртных узлов (участки дороги)
	# айди, длина, интенсивность,полученная с модели. Скорость с модели, пассажиропоток на участке транспортной сети (Нагрузка [Чел]-ОТ(ПА) из РИТМ), вместимость машин (Максимальная пропускная способность из РИТМ), геометрия 

	sql = f"""
	CREATE TABLE IF NOT EXISTS {name}
	(
		edge_id BIGINT PRIMARY KEY,
		length_m FLOAT,
		model_intensity FLOAT,
		model_speed FLOAT,
		passenger_flow FLOAT,
		capacity FLOAT,
		geometry TEXT,
		load_ratio FLOAT
	)

	"""
	with conn.cursor() as cursor:
		cursor.execute(sql)

	conn.commit()


def create_table_detectors():

	name = "detectors"


	# Таблица детекторов (Скорее всего выдадут)
	# Айди, имя, longtude (Долгота), latude(Широта)

	sql = f"""
	CREATE TABLE IF NOT EXISTS {name}
	(
		detector_id BIGINT PRIMARY KEY,
		name TEXT,
		lon FLOAT,
		lat FLOAT
	)
	"""

	with conn.cursor() as cursor:
		cursor.execute(sql)

	conn.commit()

def create_table_detectors_measurements():

	name = "detectors_measurements"

	# Таблица данных с декторов
	# Айди, время детекта, интенсивность, скорость


	sql = f"""
	CREATE TABLE IF NOT EXISTS {name}
	(
		detector_id BIGINT PRIMARY KEY,
		measured_at TIMESTAMP, 
		intensity FLOAT,
		speed FLOAT
	)
	"""

	with conn.cursor() as cursor:
		cursor.execute(sql)

	conn.commit()
	


def create_table_detectors_aggregates():

	name = "detectors_aggregates"

	# Агрегированные детекторы
	# Тип агрегации: day / hourly / weekday / monthly
	# С какого по какой (YYYY-MM-DD)
	# Средняя интенсивность
	# Средняя скорость

	sql = f"""
	CREATE TABLE IF NOT EXISTS {name}
	(
		detector_id TEXT,
		aggregate_type TEXT,
		period_value TEXT,
		avg_intensity FLOAT,
		avg_speed FLOAT,
		irregularity FLOAT
	)
	"""

	with conn.cursor() as cursor:
		cursor.execute(sql)

	conn.commit()
	


def create_table_detector_edge_mapping():

	name = "detector_edge_mapping"

	# Маппер по декторам и узлам
	# Айди детектора, айди узла, дистанция в метрах.

	sql = f"""
	CREATE TABLE IF NOT EXISTS {name}
	(
		detector_id TEXT,
		edge_id BIGINT,
		distance_m FLOAT
	)
	"""

	with conn.cursor() as cursor:
		cursor.execute(sql)

	conn.commit()

	

def create_table_detector_model_comprasion():
	name = "detector_model_comprasion"

	# Склеивание фактических данных и данных с модели
	# Айди детектора, Айди узла, реальная интенсивность, интенсивность модели, скорость модели, вместимость человек, дистанция, абсолютная ошибка, средне квадратичная ошибка

	sql = f"""
	CREATE TABLE IF NOT EXISTS {name}
	(
		detector_id TEXT,
		edge_id BIGINT,
		actual_intensity FLOAT,
		model_intensity FLOAT,
		model_speed FLOAT, 
		passenger_flow FLOAT,
		distance_m FLOAT,
		absolute_error FLOAT,
		percentage_error FLOAT
	)
	"""

	with conn.cursor() as cursor:
		cursor.execute(sql)

	conn.commit()




# Необходимы для модуля Д

def create_table_od_matrix():
	name = "od_matrix"

	# Склеивание фактических данных и данных с модели
	# Айди детектора, Айди узла, реальная интенсивность, интенсивность модели, скорость модели, вместимость человек, дистанция, абсолютная ошибка, средне квадратичная ошибка

	sql = f"""
	CREATE TABLE IF NOT EXISTS {name}
	(
		origin_id BIGINT,
		destination_id BIGINT,
		flow FLOAT
	)
	"""

	with conn.cursor() as cursor:
		cursor.execute(sql)

	conn.commit()

	


def create_table_accessibility_results():
	name = "accessibility_results"

	# Склеивание фактических данных и данных с модели
	# Айди детектора, Айди узла, реальная интенсивность, интенсивность модели, скорость модели, вместимость человек, дистанция, абсолютная ошибка, средне квадратичная ошибка

	sql = f"""
	CREATE TABLE {name}
	(
		zone_id BIGINT,
		accessibility FLOAT
	)
	"""

	with conn.cursor() as cursor:
		cursor.execute(sql)

	conn.commit()


def create_table_validation_metric(): 
	name = "validation_metrics"

	sql = f"""CREATE TABLE {name}
	(
		metric TEXT,
		value FLOAT
	)
	"""

	with conn.cursor() as cursor:
		cursor.execute(sql)

	conn.commit()



def init_db():

	create_table_detector_edge_mapping()
	create_table_detector_model_comprasion()
	create_table_detectors_aggregates()
	create_table_transport_edges()
	create_table_transport_zones()
	create_table_detectors_measurements()
	create_table_detectors()

	# Для модуля Д

	create_table_od_matrix()
	create_table_accessibility_results()
	create_table_validation_metric()

	print(f"database: {db}, has been created")

init_db()
