from pyspark.sql import SparkSession
from pyspark import SparkConf
from pyspark.sql import functions as F
from pyspark.sql.types import ArrayType, StringType
import jieba

# 创建Spark会话
conf = SparkConf() \
    .setAppName("PySpark 标题高频词统计") \
    .setMaster('spark://192.168.126.10:7077') \
    .set("spark.driver.host", "192.168.126.1")
spark = SparkSession.builder.config(conf=conf).getOrCreate()

# 读取CSV文件
df = spark.read.csv('hdfs://192.168.126.10:9000/data/ershoufang_data_processed.csv', header=True)
df = df.na.drop()

# 定义分词UDF
stopwords = ['的', '是', '和', '在', '有']
def jieba_cut(text):
    if text is None:
        return []
    return [w for w in jieba.lcut(text) if len(w) > 1 and w not in stopwords]

jieba_udf = F.udf(jieba_cut, ArrayType(StringType()))

# 分词并扁平化
words_df = df.select(F.explode(jieba_udf(F.col('标题'))).alias('word'))

# 统计词频，取前50
word_freq_df = words_df.groupBy('word').count().orderBy(F.desc('count')).limit(50)
word_freq_df.show()
# 写入MySQL新表
