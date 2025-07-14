from pyspark.sql import SparkSession
from pyspark import SparkConf
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# 创建Spark会话
conf = SparkConf() \
    .setAppName("PySpark 时间/城市均价分析") \
    .setMaster('spark://192.168.126.10:7077') \
    .set("spark.driver.host", "192.168.126.1")
spark = SparkSession.builder.config(conf=conf).getOrCreate()

# 读取CSV文件
df = spark.read.csv('hdfs://192.168.126.10:9000/data/ershoufang_data_processed.csv', header=True)
df = df.na.drop()

# 按时间分组，计算均价均值，保留2位小数
set_time = df.groupBy('时间').agg(F.round(F.avg('均价'), 2).alias('均价')).orderBy('时间')

# 添加行号，取第35-45行（含）
window = Window.orderBy('时间')
set_time_with_rownum = set_time.withColumn('rownum', F.row_number().over(window))
data_subset = set_time_with_rownum.filter((F.col('rownum') >= 35) & (F.col('rownum') <= 45)).drop('rownum')

# 按城市分组，计算均价均值，保留2位小数
city_avg_price = df.groupBy('城市').agg(F.round(F.avg('均价'), 2).alias('均价')).orderBy('城市')

# 写入MySQL新表
url = "jdbc:mysql://192.168.126.10:3306/ershoufang"
properties = {
    "user": "root",
    "password": "123456",
    "driver": "com.mysql.jdbc.Driver"
}
data_subset.coalesce(1).write.format('jdbc') \
    .option('url', url) \
    .option('dbtable', 'set_time_avg_price_subset') \
    .option('user', properties['user']) \
    .option('password', properties['password']) \
    .option('driver', properties['driver']) \
    .option('mode', 'append') \
    .save()

city_avg_price.coalesce(1).write.format('jdbc') \
    .option('url', url) \
    .option('dbtable', 'city_avg_price') \
    .option('user', properties['user']) \
    .option('password', properties['password']) \
    .option('driver', properties['driver']) \
    .option('mode', 'append') \
    .save()

print("数据已成功写入MySQL表 'set_time_avg_price_subset' 和 'city_avg_price'")
spark.stop()
