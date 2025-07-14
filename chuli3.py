from pyspark.sql import SparkSession
from pyspark import SparkConf
from pyspark.sql import functions as F
from pyspark.sql.window import Window

# 创建Spark会话
conf = SparkConf() \
    .setAppName("PySpark 户型Top5+其他统计") \
    .setMaster('spark://192.168.126.10:7077') \
    .set("spark.driver.host", "192.168.126.1")
spark = SparkSession.builder.config(conf=conf).getOrCreate()

# 读取CSV文件
df = spark.read.csv('hdfs://192.168.126.10:9000/data/ershoufang_data_processed.csv', header=True)
df = df.na.drop()

# 统计每种户型数量，降序排序
huxin_counts = df.groupBy('户型').count().orderBy(F.desc('count'))

# 取前5名
top5 = huxin_counts.limit(5)

# 取第6名及以后，合计为“其他户型”
window = F.row_number().over(Window.orderBy(F.desc('count')))
huxin_counts_with_rownum = huxin_counts.withColumn('rownum', F.row_number().over(Window.orderBy(F.desc('count'))))
other = huxin_counts_with_rownum.filter(F.col('rownum') > 5)
other_total = other.agg(F.sum('count').alias('total')).collect()[0]['total']

# 构造“其他户型”行
from pyspark.sql import Row
other_row = spark.createDataFrame([Row(户型='其他户型', count=other_total if other_total else 0)])

# 合并前5和“其他户型”
result_df = top5.unionByName(other_row)

# 重命名列
result_df = result_df.withColumnRenamed('户型', 'huxin').withColumnRenamed('count', 'total')

# 写入MySQL新表
url = "jdbc:mysql://192.168.126.10:3306/ershoufang"
properties = {
    "user": "root",
    "password": "123456",
    "driver": "com.mysql.jdbc.Driver"
}
result_df.coalesce(1).write.format('jdbc') \
    .option('url', url) \
    .option('dbtable', 'huxin_counts_modified') \
    .option('user', properties['user']) \
    .option('password', properties['password']) \
    .option('driver', properties['driver']) \
    .option('mode', 'append') \
    .save()

print("数据已成功写入MySQL表 'huxin_counts_modified'")
spark.stop()
