from pyspark.sql import SparkSession
from pyspark import SparkConf
from pyspark.sql.functions import col, regexp_extract, when
from pyspark.sql import functions as F
# 创建Spark会话
conf = SparkConf() \
    .setAppName("PySpark 的数据读写") \
    .setMaster('spark://192.168.126.10:7077') \
    .set("spark.driver.host", "192.168.126.1")
spark = SparkSession.builder.config(conf=conf).getOrCreate()

# 读取CSV文件
df = spark.read.csv('hdfs://192.168.126.10:9000/data/ershoufang_data_processed.csv', header=True)
df = df.na.drop()
city_counts = df.groupBy("城市") \
    .count() \
    .orderBy(F.desc("count")) \
    .withColumnRenamed("count", "total") \

url = "jdbc:mysql://192.168.126.10:3306/ershoufang"
properties = {
    "user": "root",
    "password": "123456",
    "driver": "com.mysql.jdbc.Driver"
}
# 写数据到MySQL的test数据库的movie表，无需预先在MySQL创建表。自动在mysql创建movie表
city_counts.coalesce(1).write.format('jdbc') \
    .option('url', url) \
    .option('dbtable', 'city_counts') \
    .option('user', properties['user']) \
    .option('password', properties['password']) \
    .option('driver', properties['driver']) \
    .option('mode', 'append') \
    # .save()  # 第一次建表时使用.save()。append为追加数据模式，overwrite覆盖数据模式

