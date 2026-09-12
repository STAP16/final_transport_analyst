import pandas as pd
from clickhouse_connect import get_client

client = get_client(
    host="localhost",
    username="click",
    password="click",
    port=8123
)