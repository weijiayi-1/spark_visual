# 目录

1. [第一章：项目背景与目标](#第一章项目背景与目标)
2. [第二章：技术选型与环境搭建](#第二章技术选型与环境搭建)
    - 2.1 技术选型
    - 2.2 依赖库与安装
3. [第三章：数据采集与初步探索](#第三章数据采集与初步探索)
    - 3.1 数据来源
    - 3.2 数据字段与样本展示
    - 3.3 HDFS 数据读取
4. [第四章：PySpark 数据清洗与统计分析](#第四章pyspark-数据清洗与统计分析)
    - 4.1 数据读取与会话创建
    - 4.2 代码解析与功能说明
    - 4.3 数据写入MySQL
5. [第五章：Django 后端接口开发](#第五章django-后端接口开发)
    - 5.1 项目结构与核心依赖
    - 5.2 MySQL 数据读取与 Pyecharts 图表生成
    - 5.3 API 设计与异常处理
6. [第六章：前端大屏可视化实现](#第六章前端大屏可视化实现)
    - 6.1 Echarts 动态渲染
    - 6.2 3D 地图与词云支持
    - 6.3 大屏布局与美化
7. [第七章：常见问题与调优](#第七章常见问题与调优)
    - 7.1 词云图不显示
    - 7.2 3D 地图不显示
    - 7.3 图表排版与样式
8. [第八章：项目总结与展望](#第八章项目总结与展望)

---

# 第一章：项目背景与目标

随着二手房市场的不断发展，数据驱动的决策变得尤为重要。如何高效地对海量二手房数据进行清洗、统计、分析，并以美观、交互性强的方式展示给用户，是数据分析师和开发者面临的共同挑战。

本项目以“广西二手房数据”为例，构建了一个集数据处理、后端接口、前端可视化于一体的全链路大屏系统。目标包括：

- 利用PySpark高效处理大规模原始房源数据，完成清洗、分组、统计等操作。
- 将分析结果写入MySQL数据库，便于后续查询与可视化。
- 使用Django后端提供RESTful API，动态生成各类可视化图表数据。
- 前端采用Echarts大屏方案，支持3D地图、3D柱状、词云、雷达、饼图、折线等多种图表，布局美观，交互流畅。
- 支持自定义分区排布、深色主题、卡片阴影、炫彩大标题等大屏美化需求。

---

# 第二章：技术选型与环境搭建

## 2.1 技术选型

- **Python**：数据处理与后端开发主力语言。
- **PySpark**：分布式数据处理，适合大规模数据清洗与统计。
- **MySQL**：关系型数据库，存储分析结果。
- **Django**：高效Web后端框架，负责API与页面渲染。
- **Pyecharts**：Python端生成Echarts配置，便于后端与前端解耦。
- **Echarts/Echarts-GL/WordCloud**：前端可视化库，支持丰富的图表类型。
- **HTML/CSS/JS**：前端页面开发。

## 2.2 依赖库与安装

### Python依赖

```bash
pip install django pymysql pyecharts pyspark
```

### 前端依赖（CDN）

- echarts: https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js
- echarts-gl: https://cdn.jsdelivr.net/npm/echarts-gl@2.0.9/dist/echarts-gl.min.js
- echarts-wordcloud: https://cdn.jsdelivr.net/npm/echarts-wordcloud@2.0.0/dist/echarts-wordcloud.min.js

### MySQL安装

- 推荐使用MySQL 5.7或8.0，需提前建库建表。

### Spark环境

- 推荐Spark 3.x，需配置好JAVA_HOME和SPARK_HOME。

---

# 第三章：数据采集与初步探索

## 3.1 数据来源

本项目的原始数据由本人通过爬虫技术从主流二手房平台（如链家、安居客等）自动化采集，涵盖广西及周边城市的二手房挂牌信息。爬取内容包括城市、户型、价格、标题、建造年份、朝向等核心字段。

**爬虫源码获取：**
- 本项目所用爬虫源码可在 [https://github.com/weijiayi-1/anjuke-crawler](https://github.com/weijiayi-1/anjuke-crawler) 获取。
- 相关博客文章详见：[https://blog.csdn.net/weijiayi040512/article/details/149136251?spm=1001.2014.3001.5502](https://blog.csdn.net/weijiayi040512/article/details/149136251?spm=1001.2014.3001.5502)

**数据采集流程简述：**
- 使用 Python 的 requests、BeautifulSoup、Selenium 等库编写爬虫脚本，自动抓取网页数据。
- 针对反爬机制，采用代理池、User-Agent 伪装、延时等手段提升爬取效率和稳定性。
- 爬取到的数据首先存储为 CSV/JSON 文件，随后上传至 HDFS（Hadoop Distributed File System），为后续大数据处理做准备。

#### 代码片段示例（简化版）：

```python
import requests
from bs4 import BeautifulSoup

url = "https://example.com/ershoufang"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")
# 解析房源信息...
```

#### 上传至 HDFS：

```bash
hdfs dfs -put ershoufang_raw.csv /user/yourname/ershoufang/
```

## 3.2 数据字段与样本展示

| 字段名   | 含义         | 示例           |
|----------|--------------|----------------|
| city     | 城市         | 南宁           |
| huxin    | 户型         | 三居           |
| price    | 总价         | 120万          |
| avg_price| 均价(元/㎡)  | 8500           |
| title    | 标题         | 南北通透学区房  |
| set_time | 建造年份     | 2005           |
| direction| 朝向         | 南             |

## 3.3 HDFS 数据读取

后续数据分析阶段，PySpark 直接从 HDFS 读取原始数据：

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName('ershoufang').getOrCreate()
df = spark.read.csv('hdfs:///user/yourname/ershoufang/ershoufang_raw.csv', header=True)
```

---

# 第四章：PySpark 数据清洗与统计分析

## 4.1 数据读取与会话创建

在每个 chuliX.py 脚本中，首先通过如下方式创建 Spark 会话，并从 HDFS 读取数据：

```python
from pyspark.sql import SparkSession
from pyspark import SparkConf

conf = SparkConf() \
    .setAppName("PySpark 任务名") \
    .setMaster('spark://192.168.126.10:7077') \
    .set("spark.driver.host", "192.168.126.1")
spark = SparkSession.builder.config(conf=conf).getOrCreate()

# 读取HDFS中的CSV数据
df = spark.read.csv('hdfs://192.168.126.10:9000/data/ershoufang_data_processed.csv', header=True)
df = df.na.drop()  # 丢弃缺失值
```

**所需库说明：**
- `pyspark`：分布式数据处理主力库
- `pyspark.sql`：结构化数据处理
- `pyspark.sql.functions`：常用SQL函数
- `pyspark.sql.window`：窗口函数（如TopN、分组排名等）

## 4.2 代码解析与功能说明

### chuli1.py：城市房源数量统计

- **功能**：统计每个城市的房源数量，结果写入MySQL表 `city_counts`。
- **核心代码**：
  ```python
  city_counts = df.groupBy("城市") \
      .count() \
      .orderBy(F.desc("count")) \
      .withColumnRenamed("count", "total")
  # 写入MySQL略
  ```

### chuli2.py：方位-城市均价统计

- **功能**：按“方位+城市”分组，计算均价平均值，保留两位小数，写入MySQL表 `direction_city_avg_price`。
- **核心代码**：
  ```python
  result_df = df.groupBy("方位", "城市") \
      .agg(F.avg("均价").alias("平均均价")) \
      .withColumn("平均均价", F.round(col("平均均价"), 2)) \
      .orderBy("方位", "城市")
  # 写入MySQL略
  ```

### chuli3.py：户型Top5+其他统计

- **功能**：统计户型数量，取前5名，其余合并为“其他户型”，写入MySQL表 `huxin_counts_modified`。
- **核心代码**：
  ```python
  huxin_counts = df.groupBy('户型').count().orderBy(F.desc('count'))
  top5 = huxin_counts.limit(5)
  # 其余合并为“其他户型”
  # unionByName合并
  ```

### chuli4.py：标题高频词统计

- **功能**：对标题字段分词，统计高频词，写入MySQL表 `title_top_keywords`。
- **核心代码**：
  ```python
  import jieba
  def jieba_cut(text):
      if text is None:
          return []
      return [w for w in jieba.lcut(text) if len(w) > 1 and w not in stopwords]
  jieba_udf = F.udf(jieba_cut, ArrayType(StringType()))
  words_df = df.select(F.explode(jieba_udf(F.col('标题'))).alias('word'))
  word_freq_df = words_df.groupBy('word').count().orderBy(F.desc('count')).limit(50)
  # 写入MySQL略
  ```

### chuli5.py：建造年份与城市均价统计

- **功能**：分时间段统计均价（取第35-45年），以及各城市均价，分别写入MySQL表 `set_time_avg_price_subset` 和 `city_avg_price`。
- **核心代码**：
  ```python
  set_time = df.groupBy('时间').agg(F.round(F.avg('均价'), 2).alias('均价')).orderBy('时间')
  # 取第35-45行
  window = Window.orderBy('时间')
  set_time_with_rownum = set_time.withColumn('rownum', F.row_number().over(window))
  data_subset = set_time_with_rownum.filter((F.col('rownum') >= 35) & (F.col('rownum') <= 45)).drop('rownum')
  # 写入MySQL略
  ```

## 4.3 数据写入MySQL

每个脚本最后都通过如下方式将结果写入MySQL：

```python
url = "jdbc:mysql://192.168.126.10:3306/ershoufang"
properties = {
    "user": "root",
    "password": "123456",
    "driver": "com.mysql.jdbc.Driver"
}
result_df.coalesce(1).write.format('jdbc') \
    .option('url', url) \
    .option('dbtable', '目标表名') \
    .option('user', properties['user']) \
    .option('password', properties['password']) \
    .option('driver', properties['driver']) \
    .option('mode', 'append') \
    .save()
```

---

# 第五章：Django 后端接口开发

## 5.1 项目结构与核心依赖

本项目后端采用 Django 框架，负责 API 提供和页面渲染。主要依赖如下：

- `Django`：Web 框架
- `pymysql`：MySQL 数据库驱动
- `pyecharts`：Python 端生成 Echarts 配置项

项目结构示例：

```
visual_screen/
  charts/
    views.py
    urls.py
    templates/
      charts/
        chart.html
```

## 5.2 MySQL 数据读取与 Pyecharts 图表生成

以 `views.py` 为例，后端通过 pymysql 连接 MySQL，读取分析结果表，并用 pyecharts 生成各类图表 option：

```python
import pymysql
from pyecharts.charts import Bar
from pyecharts import options as opts

def get_city_counts():
    connection = pymysql.connect(
        host='192.168.126.10',
        user='root',
        password='123456',
        database='ershoufang',
        charset='utf8mb4'
    )
    with connection.cursor() as cursor:
        cursor.execute("SELECT 城市, total FROM city_counts ORDER BY total DESC")
        results = cursor.fetchall()
        cities = [row[0] for row in results]
        counts = [row[1] for row in results]
    connection.close()
    return cities, counts

def generate_bar_chart():
    cities, counts = get_city_counts()
    bar = (
        Bar()
        .add_xaxis(cities)
        .add_yaxis("房源数量", counts)
        .set_global_opts(title_opts=opts.TitleOpts(title="各城市房源数量对比"))
    )
    return bar
```

## 5.3 API 设计与异常处理

后端通过 `/charts/data/` API 返回所有图表的 option，前端 fetch 后渲染：

```python
from django.http import JsonResponse

def chart_data(request):
    bar = generate_bar_chart()
    # 其它图表略
    return JsonResponse({
        "bar_chart_data": bar.dump_options(),
        # 其它图表数据
    })
```

异常时返回兜底示例数据，保证前端不报错。

---

# 第六章：前端大屏可视化实现

## 6.1 Echarts 动态渲染

前端页面 `chart.html` 通过 fetch 拉取后端数据，动态渲染各类图表：

```javascript
fetch('/charts/data/')
    .then(response => response.json())
    .then(data => {
        echarts.init(document.getElementById('barChart')).setOption(eval('(' + data.bar_chart_data + ')'));
        // 其它图表渲染
    });
```

## 6.2 3D 地图与词云支持

- 3D 地图需动态 fetch geojson 并注册：
  ```javascript
  fetch('https://geo.datav.aliyun.com/areas_v3/bound/450000_full.json')
      .then(res => res.json())
      .then(geoJson => {
          echarts.registerMap('广西', geoJson);
          echarts.init(document.getElementById('map3dChart')).setOption(...);
      });
  ```
- 词云需引入 echarts-wordcloud 插件。

## 6.3 大屏布局与美化

- 使用 flex 布局分区（左/中/右/底部）
- 深色背景、卡片阴影、炫彩大标题
- 图表容器尺寸按需设置，保证视觉统一

---

# 第七章：常见问题与调优

## 7.1 词云图不显示

- 检查前端是否引入 echarts-wordcloud
- 后端词频归一化，避免极大值导致前端渲染异常

## 7.2 3D 地图不显示

- 检查 geojson 是否正确注册
- 地图容器尺寸是否足够

## 7.3 图表排版与样式

- 多次调整 flex、margin、width/height，确保与设计稿一致
- 标题、图例、标签等细节统一风格

---

# 第八章：项目总结与展望

本项目实现了从数据采集、HDFS 存储、PySpark 清洗、MySQL 入库，到 Django+Pyecharts 后端接口、Echarts 前端大屏的全链路数据可视化。  
**亮点：**
- 全流程自动化，数据链路清晰
- 支持多种复杂图表（3D、词云、雷达等）
- 大屏美观、交互流畅，易于扩展

**展望：**
- 可接入实时数据流，支持动态刷新
- 增加更多交互功能（筛选、联动等）
- 支持多端适配与响应式布局

---

如需对某一节进一步细化（如详细代码讲解、性能优化、部署上线等），请告诉我具体章节或需求！ 