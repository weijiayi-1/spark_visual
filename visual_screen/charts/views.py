from django.shortcuts import render
from django.http import JsonResponse
from pyecharts import options as opts
from pyecharts.charts import Bar, Map3D, Bar3D, Radar, Pie, WordCloud, Line
from pyecharts.globals import ThemeType, ChartType
from pyecharts.commons.utils import JsCode
import pymysql
import json

def get_city_counts():
    """从MySQL数据库获取各城市房源数量数据"""
    try:
        connection = pymysql.connect(
            host='192.168.126.10',
            port=3306,
            user='root',
            password='123456',
            database='ershoufang',
            charset='utf8mb4'
        )
        with connection.cursor() as cursor:
            sql = """
            SELECT 城市, total 
            FROM city_counts 
            ORDER BY total DESC
            """
            cursor.execute(sql)
            results = cursor.fetchall()
            cities = []
            counts = []
            for row in results:
                cities.append(row[0])
                counts.append(row[1])
        connection.close()
        return cities, counts
    except Exception as e:
        print(f"数据库连接错误: {e}")
        return ['北京', '上海', '广州', '深圳', '杭州'], [1200, 980, 850, 720, 650]

def get_guangxi_city_counts():
    # 这里模拟数据，实际可从数据库查广西各市
    return [
        ("南宁", 100), ("柳州", 80), ("桂林", 60), ("梧州", 50), ("北海", 40),
        ("防城港", 30), ("钦州", 35), ("贵港", 25), ("玉林", 28), ("百色", 20),
        ("贺州", 18), ("河池", 15), ("来宾", 12), ("崇左", 10)
    ]

def get_city_avg_price():
    """从MySQL获取城市均价数据"""
    try:
        connection = pymysql.connect(
            host='192.168.126.10',
            port=3306,
            user='root',
            password='123456',
            database='ershoufang',
            charset='utf8mb4'
        )
        with connection.cursor() as cursor:
            sql = """
            SELECT 城市, 均价
            FROM city_avg_price
            ORDER BY 均价 DESC
            """
            cursor.execute(sql)
            results = cursor.fetchall()
            cities = [row[0] for row in results]
            prices = [float(row[1]) for row in results]
            return cities, prices
    except Exception as e:
        print(f"数据库连接错误: {e}")
        # 返回示例数据
        return ['南宁', '柳州', '桂林'], [8000, 7000, 6000]

def get_huxin_counts_modified():
    """从MySQL获取户型数量数据"""
    try:
        connection = pymysql.connect(
            host='192.168.126.10',
            port=3306,
            user='root',
            password='123456',
            database='ershoufang',
            charset='utf8mb4'
        )
        with connection.cursor() as cursor:
            sql = """
            SELECT huxin, total
            FROM huxin_counts_modified
            """
            cursor.execute(sql)
            results = cursor.fetchall()
            huxin_list = [row[0] for row in results]
            total_values = [int(row[1]) for row in results]
            return huxin_list, total_values
    except Exception as e:
        print(f"数据库连接错误: {e}")
        return ['一居', '二居', '三居', '四居', '其他户型'], [100, 200, 300, 150, 50]

def get_year_price_subset():
    """从MySQL获取建造年份与均价数据（第35-45年）"""
    try:
        connection = pymysql.connect(
            host='192.168.126.10',
            port=3306,
            user='root',
            password='123456',
            database='ershoufang',
            charset='utf8mb4'
        )
        with connection.cursor() as cursor:
            sql = """
            SELECT 时间, 均价
            FROM set_time_avg_price_subset
            ORDER BY 时间
            """
            cursor.execute(sql)
            results = cursor.fetchall()
            years = [str(row[0]) for row in results]
            prices = [float(row[1]) for row in results]
            return years, prices
    except Exception as e:
        print(f"数据库连接错误: {e}")
        return ['2000', '2001', '2002'], [5000, 5200, 5400]

guangxi_coords = {
    "南宁市": [108.479, 23.1152],
    "柳州市": [109.4282, 24.3269],
    "桂林市": [110.3055, 25.2736],
    "梧州市": [111.3055, 23.4856],
    "北海市": [109.1369, 21.4813],
    "防城港市": [108.3636, 21.6869],
    "钦州市": [108.6388, 21.9817],
    "贵港市": [109.6137, 23.1118],
    "玉林市": [110.1647, 22.6366],
    "百色市": [106.6318, 23.9013],
    "贺州市": [111.5526, 24.4116],
    "河池市": [108.0854, 24.6929],
    "来宾市": [109.2318, 23.7418],
    "崇左市": [107.3579, 22.4151]
}

def get_word_freq():
    """从MySQL获取标题关键词及频率"""
    try:
        connection = pymysql.connect(
            host='192.168.126.10',
            port=3306,
            user='root',
            password='123456',
            database='ershoufang',
            charset='utf8mb4'
        )
        with connection.cursor() as cursor:
            sql = """
            SELECT word, count
            FROM title_top_keywords
            """
            cursor.execute(sql)
            results = cursor.fetchall()
            word_freq = [(row[0], int(row[1])) for row in results]
            return word_freq
    except Exception as e:
        print(f"数据库连接错误: {e}")
        return [("二手房", 100), ("学区", 80), ("地铁", 60), ("南北通透", 50), ("精装修", 40)]

def generate_wordcloud_chart():
    word_freq = get_word_freq()
    wordcloud = (
        WordCloud()
        .add(
            series_name="标题关键词",
            data_pair=word_freq,
            word_size_range=[12, 60],
            shape="circle",
            mask_image=None,
            word_gap=10,
            rotate_step=45,
            tooltip_opts=opts.TooltipOpts(
                formatter="{b}: {c}"
            )
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="标题关键词词云", title_textstyle_opts=opts.TextStyleOpts(color="#00ffe7")),
            tooltip_opts=opts.TooltipOpts(is_show=True)
        )
    )
    return wordcloud

def generate_year_line_chart():
    years, prices = get_year_price_subset()
    line = (
        Line(init_opts=opts.InitOpts(width="1000px", height="500px"))
        .add_xaxis(years)
        .add_yaxis(
            series_name="",
            y_axis=prices,
            symbol="circle",
            symbol_size=8,
            label_opts=opts.LabelOpts(is_show=True),
            linestyle_opts=opts.LineStyleOpts(width=3),
            itemstyle_opts=opts.ItemStyleOpts(color="#FF6600")
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="广西二手房建造年份与均价关系",
                subtitle="数据范围：第35-45年",
                pos_left="center",
                pos_top="10px",
                title_textstyle_opts=opts.TextStyleOpts(color="#00ffe7")
            ),
            xaxis_opts=opts.AxisOpts(
                name="建造年份",
                axislabel_opts=opts.LabelOpts(rotate=45)
            ),
            yaxis_opts=opts.AxisOpts(
                name="均价（元/㎡）",
                splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                formatter="{b}年<br/>均价: {c}元/㎡"
            )
        )
    )
    return line

def get_direction_city_avg_price():
    """从MySQL获取方位-城市-均价数据"""
    try:
        connection = pymysql.connect(
            host='192.168.126.10',
            port=3306,
            user='root',
            password='123456',
            database='ershoufang',
            charset='utf8mb4'
        )
        with connection.cursor() as cursor:
            sql = """
            SELECT 方位, 城市, 平均均价
            FROM direction_city_avg_price
            """
            cursor.execute(sql)
            results = cursor.fetchall()
            data = []
            directions = set()
            cities = set()
            for row in results:
                directions.add(row[0])
                cities.add(row[1])
            directions = sorted(list(directions))
            cities = sorted(list(cities))
            direction_to_idx = {d: i for i, d in enumerate(directions)}
            city_to_idx = {c: i for i, c in enumerate(cities)}
            for row in results:
                x_idx = direction_to_idx[row[0]]
                y_idx = city_to_idx[row[1]]
                data.append([x_idx, y_idx, float(row[2])])
            return data, directions, cities
    except Exception as e:
        print(f"数据库连接错误: {e}")
        # 返回示例数据
        directions = ['东', '南', '西', '北']
        cities = ['南宁', '柳州', '桂林']
        data = [
            [0, 0, 8000], [1, 0, 8200], [2, 0, 7800], [3, 0, 8100],
            [0, 1, 7000], [1, 1, 7200], [2, 1, 6900], [3, 1, 7100],
            [0, 2, 6000], [1, 2, 6200], [2, 2, 5900], [3, 2, 6100],
        ]
        return data, directions, cities

def generate_huxin_radar_chart():
    huxin_list, total_values = get_huxin_counts_modified()
    max_value = max(total_values) + 200
    schema = [{"name": huxin, "max": max_value} for huxin in huxin_list]
    radar = (
        Radar(init_opts=opts.InitOpts(width="800px", height="500px"))
        .add_schema(schema=schema)
        .add(
            series_name="户型数量",
            data=[total_values],
            color="#FF6600",
            areastyle_opts=opts.AreaStyleOpts(opacity=0.3),
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False),  # 隐藏数值标签
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))  # 再次确保隐藏
        .set_global_opts(
            title_opts=opts.TitleOpts(title="户型数量对比雷达图", title_textstyle_opts=opts.TextStyleOpts(color="#00ffe7")),
            legend_opts=opts.LegendOpts(is_show=False)
        )
    )
    return radar

def generate_huxin_pie_chart():
    huxin_list, total_values = get_huxin_counts_modified()
    data_pie = list(zip(huxin_list, total_values))
    pie = (
        Pie(init_opts=opts.InitOpts(width="800px", height="600px"))
        .add(
            series_name="户型分布",
            data_pair=data_pie,
            radius=["0%", "70%"],
            center=["50%", "50%"],
            label_opts=opts.LabelOpts(
                formatter="{b}: {c} ({d}%)",
                font_size=12,
                color="#333"
            ),
            itemstyle_opts=opts.ItemStyleOpts(
                border_width=1,
                border_color="#fff"
            )
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="户型分布饼图",
                subtitle=f"总计 {sum(total_values)} 套房源",
                pos_left="center",
                title_textstyle_opts=opts.TextStyleOpts(color="#00ffe7")
            ),
            legend_opts=opts.LegendOpts(is_show=False),  # 隐藏图例
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                formatter="{a}<br/>{b}: {c} ({d}%)"
            )
        )
        .set_series_opts(
            emphasis_opts=opts.EmphasisOpts(
                label_opts=opts.LabelOpts(font_size=14)
            )
        )
    )
    return pie

def generate_bar_chart():
    cities, counts = get_city_counts()
    bar = (
        Bar(init_opts=opts.InitOpts(width="400px", height="300px"))
        .add_xaxis(cities)
        .add_yaxis(
            series_name="房源数量",
            y_axis=counts,
            label_opts=opts.LabelOpts(is_show=False),  # 隐藏数值标签
            itemstyle_opts=opts.ItemStyleOpts(color="#5470C6")
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="各城市房源数量对比",
                pos_left="center",
                pos_top="20px",
                title_textstyle_opts=opts.TextStyleOpts(color="#00ffe7")  # 标题颜色
            ),
            xaxis_opts=opts.AxisOpts(
                name="城市",
                axislabel_opts=opts.LabelOpts(rotate=0)
            ),
            yaxis_opts=opts.AxisOpts(
                name="房源数量（套）",
                splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                formatter="{b}<br/>数量: {c}套"
            ),
            legend_opts=opts.LegendOpts(is_show=False)
        )
    )
    return bar

def generate_city_bar_chart():
    cities, prices = get_city_avg_price()
    bar = (
        Bar(init_opts=opts.InitOpts(width="400px", height="300px"))
        .add_xaxis(cities)
        .add_yaxis(
            series_name="",
            y_axis=prices,
            label_opts=opts.LabelOpts(is_show=False),  # 隐藏数值标签
            itemstyle_opts=opts.ItemStyleOpts(color="#37A2FF"),
            bar_width="40%"
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="各城市二手房均价对比",
                pos_left="center",
                title_textstyle_opts=opts.TextStyleOpts(color="#00ffe7")  # 标题颜色
            ),
            xaxis_opts=opts.AxisOpts(
                name="城市",
                axislabel_opts=opts.LabelOpts(
                    rotate=30,
                    interval=0
                )
            ),
            yaxis_opts=opts.AxisOpts(
                name="均价（元/㎡）",
                splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                formatter="{b}<br/>均价: {c}元/㎡"
            ),
            datazoom_opts=[opts.DataZoomOpts()],
            legend_opts=opts.LegendOpts(is_show=False)
        )
    )
    return bar

def generate_map3d_chart():
    city_counts = get_guangxi_city_counts()
    map3d_data = []
    for city, total in city_counts:
        city_name = city + "市"
        if city_name in guangxi_coords:
            height = total / 5
            map3d_data.append((city_name, [guangxi_coords[city_name][0], guangxi_coords[city_name][1], height]))
    map3d = (
        Map3D(init_opts=opts.InitOpts(width="1000px", height="600px"))
        .add_schema(
            maptype="广西",
            itemstyle_opts=opts.ItemStyleOpts(
                color="rgb(5,101,123)",
                opacity=1,
                border_width=0.8,
                border_color="rgb(62,215,213)",
            ),
            map3d_label=opts.Map3DLabelOpts(
                is_show=False,
                formatter=JsCode("function(data){return data.name + ' ' + data.value[2];}"),
            ),
            emphasis_label_opts=opts.LabelOpts(
                is_show=False,
                color="#fff",
                font_size=10,
                background_color="rgba(0,23,11,0)",
            ),
            light_opts=opts.Map3DLightOpts(
                main_color="#fff",
                main_intensity=1.2,
                main_shadow_quality="high",
                is_main_shadow=False,
                main_beta=10,
                ambient_intensity=0.3,
            ),
        )
        .add(
            series_name="二手房总数/5",
            data_pair=map3d_data,
            type_=ChartType.BAR3D,
            bar_size=1,
            shading="lambert",
            label_opts=opts.LabelOpts(
                is_show=False,
                formatter=JsCode("function(data){return data.name + ' ' + data.value[2];}"),
            ),
        )
        .set_global_opts(title_opts=opts.TitleOpts(title="广西二手房数据分布", title_textstyle_opts=opts.TextStyleOpts(color="#00ffe7")))
    )
    return map3d

def generate_bar3d_chart():
    data, directions, cities = get_direction_city_avg_price()
    if not data:
        return Bar3D().set_global_opts(title_opts=opts.TitleOpts(title="无数据", title_textstyle_opts=opts.TextStyleOpts(color="#00ffe7")))
    bar3d = (
        Bar3D(init_opts=opts.InitOpts(width="1200px", height="800px"))
        .add(
            series_name="均价(元/㎡)",
            data=data,
            xaxis3d_opts=opts.Axis3DOpts(
                type_="category",
                data=directions,
                name="方位",
                axislabel_opts=opts.LabelOpts(interval=0, rotate=0)
            ),
            yaxis3d_opts=opts.Axis3DOpts(
                type_="category",
                data=cities,
                name="城市",
                axislabel_opts=opts.LabelOpts(interval=0, rotate=45, font_size=10)
            ),
            zaxis3d_opts=opts.Axis3DOpts(type_="value", name="均价"),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="各城市不同方位房价分布3D图", title_textstyle_opts=opts.TextStyleOpts(color="#00ffe7")),
            visualmap_opts=opts.VisualMapOpts(
                max_=max([d[2] for d in data]),
                min_=min([d[2] for d in data]),
                range_color=[
                    "#313695", "#4575b4", "#74add1", "#abd9e9", "#e0f3f8",
                    "#ffffbf", "#fee090", "#fdae61", "#f46d43", "#d73027", "#a50026"
                ],
            ),
            tooltip_opts=opts.TooltipOpts()
        )
    )
    return bar3d

def chart_view(request):
    return render(request, 'charts/chart.html')

def chart_data(request):
    bar = generate_bar_chart()
    map3d = generate_map3d_chart()
    bar3d = generate_bar3d_chart()
    city_bar = generate_city_bar_chart()
    huxin_radar = generate_huxin_radar_chart()
    huxin_pie = generate_huxin_pie_chart()
    wordcloud = generate_wordcloud_chart()
    year_line = generate_year_line_chart()
    return JsonResponse({
        "bar_chart_data": bar.dump_options(),
        "map3d_chart_data": map3d.dump_options(),
        "bar3d_chart_data": bar3d.dump_options(),
        "city_bar_chart_data": city_bar.dump_options(),
        "huxin_radar_chart_data": huxin_radar.dump_options(),
        "huxin_pie_chart_data": huxin_pie.dump_options(),
        "wordcloud_chart_data": wordcloud.dump_options(),
        "year_line_chart_data": year_line.dump_options()
    })
