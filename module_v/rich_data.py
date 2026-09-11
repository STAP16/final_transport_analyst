import pandas as pd
from pandas import DataFrame

from clickhouse_connect import get_client

client = get_client(host="localhost", username="click", password="click", port=8123)

db = "transport"

# Здесь мы формируем несколько dataframe из одного, чтобы потом записать их в соотвествующие таблицы в Clickhouse

df = pd.read_csv(r"module_v\detectors.csv")

df.dropna()

df["timestamp"] = pd.to_datetime(df["timestamp"])

#Нужно сделать признаки периода
df["date"] = df["timestamp"].dt.date
df["week"] = df["timestamp"].dt.isocalendar().week
df["month"] = df["timestamp"].dt.month
df["year"] = df["timestamp"].dt.year
df["hour"] = df["timestamp"].dt.hour
df["weekday"] = df["timestamp"].dt.day_name()

def create_aggregation_dataframe(
    group_by: list[str],
    aggregation_type: str,
    calculate_irregularity: bool = False,
) -> DataFrame:

    agg_df = (
        df.groupby(["detector_id", *group_by], as_index=False)
        .agg(
            avg_intensity=("intensity", "mean"),
            avg_speed=("speed", "mean"),
        )
    )

    agg_df["aggregate_type"] = aggregation_type

    agg_df["period_value"] = (
        agg_df[group_by]
        .astype(str)
        .agg("-".join, axis=1)
    )

    if calculate_irregularity:
        total = (
            agg_df.groupby("detector_id")["avg_intensity"]
            .transform("sum")
        )

        agg_df["irregularity"] = (
            agg_df["avg_intensity"] / total
        )
    else:
        agg_df["irregularity"] = None

    return agg_df


hourly = create_aggregation_dataframe(["hour"], "hour", True)
weekday_profile = create_aggregation_dataframe(["weekday"], "weekday")
daily = create_aggregation_dataframe(["date"], "date")
weekly = create_aggregation_dataframe(["week"], "week")
monthly = create_aggregation_dataframe(["month", "year"], "month")

yearly =  create_aggregation_dataframe(["year"], "year")


columns = [
	"detector_id",
	"aggregate_type",
	"period_value",
	"avg_intensity",
	"avg_speed",
    "irregularity"
]
aggregates = pd.concat(
	[
	daily[columns],
	hourly[columns],
	monthly[columns],
	yearly[columns],
	weekday_profile[columns],
	weekly[columns]
	], ignore_index=True
)

aggregates["detector_id"] = aggregates["detector_id"].astype(str)
aggregates["aggregate_type"] = aggregates["aggregate_type"].astype(str)
aggregates["period_value"] = aggregates["period_value"].astype(str)

aggregates["avg_intensity"] = aggregates["avg_intensity"].astype(float)
aggregates["avg_speed"] = aggregates["avg_speed"].astype(float)

client.insert_df(f"{db}.detectors_aggregates", aggregates)
print("Всавка выполнена успешно: ", len(aggregates))