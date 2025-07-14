from pyspark.sql import SparkSession
from pyspark import SparkConf
from pyspark.sql.functions import col, round as spark_round
from pyspark.sql import functions as F

# 创建Spark会话
conf = SparkConf() \
    .setAppName("PySpark 方位城市均价分析") \
    .setMaster('spark://192.168.126.10:7077') \
    .set("spark.driver.host", "192.168.126.1")
spark = SparkSession.builder.config(conf=conf).getOrCreate()

# 读取CSV文件
df = spark.read.csv('hdfs://192.168.126.10:9000/data/ershoufang_data_processed.csv', header=True)
df = df.na.drop()

# 对数据进行分组处理：按方位和城市分组，计算均价平均值并保留2位小数
result_df = df.groupBy("方位", "城市") \
    .agg(F.avg("均价").alias("平均均价")) \
    .withColumn("平均均价", spark_round(col("平均均价"), 2)) \
    .orderBy("方位", "城市")

# MySQL连接配置
url = "jdbc:mysql://192.168.126.10:3306/ershoufang"
properties = {
    "user": "root",
    "password": "123456",
    "driver": "com.mysql.jdbc.Driver"
}

# 写数据到MySQL的新表
result_df.coalesce(1).write.format('jdbc') \
    .option('url', url) \
    .option('dbtable', 'direction_city_avg_price') \
    .option('user', properties['user']) \
    .option('password', properties['password']) \
    .option('driver', properties['driver']) \
    .option('mode', 'append') \
    .save()  # 第一次建表时使用.save()。append为追加数据模式，overwrite覆盖数据模式

print("数据已成功写入MySQL表 'direction_city_avg_price'")
spark.stop()
