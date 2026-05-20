import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F

## Initialization
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

BUCKET = "mexico-public-safety-observatory"

# 1. Read raw data --------------------------------

delitos = spark.read.csv(
    f"s3://{BUCKET}/raw/delitos.csv",
    header=True,
    inferSchema=True
)

pob = spark.read.csv(
    f"s3://{BUCKET}/raw/pob.csv",
    header=True,
    inferSchema=True
)

# 2. Pivot months wide → long ---------------------------------------------

months = ["enero","febrero","marzo","abril","mayo","junio",
          "julio","agosto","septiembre","octubre","noviembre","diciembre"]

# Melt the 12 month columns into a single column
delitos_long = delitos.unpivot(
    ids=["año", "entidad_clave", "entidad_nombre",
         "bien_juridico_afectado", "tipo_delito",
         "subtipo_delito", "modalidad", "sexo", "rango_edad"],
    values=months,
    variableColumnName="month_name",
    valueColumnName="count"
)

# Map month name to month number
month_map = {m: i+1 for i, m in enumerate(months)}
month_map_expr = F.create_map([F.lit(x) for pair in month_map.items() for x in pair])

delitos_long = delitos_long.withColumn("month", month_map_expr[F.col("month_name")]) \
                           .drop("month_name")

# 3. Aggregate by state-year-month-crime_type --------------------------------

delitos_agg = delitos_long.groupBy(
    "año", "month", "entidad_clave", "entidad_nombre", "tipo_delito"
).agg(
    F.sum("count").alias("total_count")
)

# 4. Join with population (males + females combined) -------------------------

pop_total = pob.groupBy("clave_ent", "nom_ent", "anio").agg(
    F.sum("poblacion").alias("total_population")
)

delitos_pop = delitos_agg.join(
    pop_total,
    (delitos_agg.entidad_clave == pop_total.clave_ent) &
    (delitos_agg.año == pop_total.anio),
    how="left"
).drop("clave_ent", "anio")

# 5. Calculate rate per 100,000 inhabitants ----------------------------------

delitos_pop = delitos_pop.withColumn(
    "rate_per_100k",
    (F.col("total_count") / F.col("total_population")) * 100000
)

# 6. Save to processed/ as Parquet --------------------------------------------

delitos_pop.write.mode("overwrite").parquet(
    f"s3://{BUCKET}/processed/delitos_rate/"
)

job.commit()