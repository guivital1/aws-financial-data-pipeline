"""AWS Glue job that converts raw BCB JSON Lines into partitioned Parquet."""

from awsglue.utils import getResolvedOptions
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)
import sys


args = getResolvedOptions(sys.argv, ["JOB_NAME", "RAW_PATH", "CURATED_PATH"])
spark = SparkSession.builder.appName(args["JOB_NAME"]).getOrCreate()

schema = StructType(
    [
        StructField("series_id", IntegerType(), False),
        StructField("series_slug", StringType(), False),
        StructField("series_name", StringType(), False),
        StructField("frequency", StringType(), False),
        StructField("unit", StringType(), False),
        StructField("observation_date", StringType(), False),
        StructField("year", IntegerType(), False),
        StructField("month", IntegerType(), False),
        StructField("value", DoubleType(), False),
        StructField("raw_value", StringType(), False),
        StructField("source", StringType(), False),
        StructField("source_url", StringType(), False),
        StructField("ingested_at", StringType(), False),
    ]
)

raw = spark.read.schema(schema).json(args["RAW_PATH"])
curated = (
    raw.withColumn("observation_date", F.to_date("observation_date"))
    .withColumn("ingested_at", F.to_timestamp("ingested_at"))
    .dropDuplicates(["series_id", "observation_date"])
)

if curated.filter(F.col("observation_date").isNull() | F.col("value").isNull()).limit(1).count():
    raise ValueError("Curated dataset contains invalid required fields")

(
    curated.write.mode("overwrite")
    .partitionBy("series_slug", "year", "month")
    .parquet(args["CURATED_PATH"])
)
