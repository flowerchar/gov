# 市州区县词频统计

本项目从[贵州省人民政府市县动态](https://www.guizhou.gov.cn/home/sxdt)以及[贵州省投资促进局地方动态](http://invest.guizhou.gov.cn/dtzx/gzdt/dfdt/)爬取所有地方动态的数据，并将数据保存到MySQL里面。通过tkinter由用户自主选择时间段，程序将从数据库里检索出相应的记录，并返回到前端界面上，还会统计取出来的数据里，哪些市州区县（通过jieba分词）出现的频次比较多，以此为依据用wordcloud生成词云图

1. 运行初始界面：

   ![image-20230412150633546](README.assets/image-20230412150633546.png)

2. 查询近三年的记录：

   ![image-20230412150736614](README.assets/image-20230412150736614.png)

3. 生成的词云图：

   ![image-20230316143047003](README.assets/image-20230316143047003.png)
   
   以及词频excel表格：
   
   ![image-20230412150846087](README.assets/image-20230412150846087.png)

本项目主要由三部分模块组成：

## 1.spider

在该模块下，主要功能由核心类GovSpider完成，有以下方法：

- get_gov_name：爬取贵州省所有的市州区县
- spider_gov：爬取贵州省人民政府网的地方动态
- spider_invest：爬取贵州省投资促进局的地方动态

同时可以在实例化GovSpider的时候，传入指定的url和xpath规则，调用上述方法依然能爬取到指定的数据

> 除开市州区县的数据外，省政府以及投资促进局的数据都是一个二维列表，每一个元素包含标题，URL链接以及日期

## 2.database

在该模块下，主要功能由核心类useDBStore完成，有以下方法：

- keep_in_mysql：将爬取到的政务数据保存到MySQL里面
- keep_in_mysql2：将爬取到的市州区县数据保存到MySQL
- search_mysql：按照给定的时间字符串，查询出符合要求的政务数据
- location_mysql：从数据库里检索出所有的地区
- jieba_process：通过jieba处理分词
- draw_cloud：根据上述流程处理后，生成对应的词云图

在实例化useDBStore的时候，可以传入自定义的数据库配置信息，并且由于jieba不能区分碧江跟西秀是一个地区名，需要加载一个文本文件表明

以下是wordcloud的一些坑：
> 一般都是从字符串的文本你来生成词云图，但是wordcloud也提供了generate_from_frequencied作为字典频次传入
>
> 当词云图出现两次重复词组时，WordCloud参数里加上collocations=False即可解决
>
> 不能正常显示中文字符时，需要制定中文的font_path

## 3.interface

该模块通过tkinter构建一个简易的交互界面，通过与database交互，将满足用户查询条件的数据从数据库检索出来，并渲染到界面上



## 4.设计流程

### 4.1 爬虫模块

打开贵州省人民政府网站首页>新闻>市县动态，右键检查点击第一个标题得到如下：

![image-20230412140648100](README.assets/image-20230412140648100.png)

可以发现超链接的标题跟URL都封装在li标签下面的a标签的title和href属性，日期封装在li标签下的span标签的文本属性，那么拿到当前页的所有数据只需要拿到所有li标签的上一级ul标签。ul的父标签是<div class="PageMainBox aBox">，在Python里面解析数据有两种主流的第三方库：BeautifulSoup和lxml。BeautifulSoup和lxml都是Python中用于处理XML和HTML的解析库。它们都能够将HTML或XML文档解析为树形结构，方便对其中的元素进行操作和提取。虽然它们的功能有一些重叠，但是它们在实现细节和性能上存在一些差异：

1. 简单易用性：BeautifulSoup非常易于使用，特别是对于初学者而言。它提供了简单的API，易于提取HTML或XML中的内容。lxml的使用稍微复杂一些，需要熟悉XPath语法才能进行高级操作。
2. 性能：lxml在解析HTML或XML文档时比BeautifulSoup更快。它是用C语言实现的，而BeautifulSoup则是用Python实现的。
3. 兼容性：BeautifulSoup比lxml更加宽松，可以处理不规范的HTML或XML文档。而lxml则需要遵循严格的标准，对于不规范的文档可能会出现解析错误。
4. 功能扩展性：lxml可以通过插件机制进行功能扩展，可以添加新的解析器和序列化器。而BeautifulSoup则没有这个功能。

如果需要快速提取HTML或XML中的内容，并且文档比较简单，可以选择使用BeautifulSoup。如果需要处理复杂的XML或HTML文档，并且对性能有较高要求，可以选择使用lxml。这里选择lxml来解析数据，但是div的属性一共有两个PageMainBox和aBox，需要使用contains这种特殊语法，那么获取所有符合的a标签和所有span标签的lxml规则就是：

> ```python
> gov_rule = '//div[contains(@class,"PageMainBox")]//a',
> gov_rule2 = '//div[contains(@class,"PageMainBox")]//span/text()'
> ```

点击下一页，发现url改变为：https://www.guizhou.gov.cn/home/sxdt/index_1.html，点击第三页url为：https://www.guizhou.gov.cn/home/sxdt/index_2.html，...，点击最后一页url为：https://www.guizhou.gov.cn/home/sxdt/index_49.html。可以总结出规律：一共五十页，首页的Url结尾是/index.html，第n页的url结尾是/index_{n-1}.html，那么可以在程序中设计一个for循环把所有页的数据爬取下来：

```python
def spider_gov(self)->list:
    '''
    爬取贵州省人民政府网站地方动态的数据
    :return:包含地方动态的标题，链接，日期
    '''
    data = [] # 包含地方动态的标题，链接，日期
    resp = requests.get(url=self.gov_url) # 向首页发起请求
    resp.encoding = resp.apparent_encoding # 设置文本编码格式
    html = etree.HTML(resp.text) # 解析文本
    a_s = html.xpath(self.gov_rule) # 传入规则，得到标题和链接
    date_s = html.xpath(self.gov_rule2) # 传入规则，得到日期
    for i, j in zip(a_s, date_s): 
        data.append([i.attrib.get('title'), i.attrib.get('href'), ''.join(j).strip()])
        print([i.attrib.get('title'), i.attrib.get('href'), ''.join(j).strip()])
    for i in tqdm(range(1, 51)): # tqdm会显示程序进度
        new_url = f'https://www.guizhou.gov.cn/home/sxdt/index_{i}.html' # 字符串拼接拿到所有非首页
        new_resp = requests.get(new_url) # 向每一页发起请求
        new_resp.encoding = new_resp.apparent_encoding # 将乱码处理为中文字符
        new_html = etree.HTML(new_resp.text) # 把文本交给lxml解析
        new_a_s = new_html.xpath(self.gov_rule) # 按照指定规则解析文本（a标签的）,存入一个列表
        new_date_s = new_html.xpath(self.gov_rule2) # 按照指定规则解析文本（span标签的）,存入一个列表
        for m, n in zip(new_a_s, new_date_s): # zip函数同时遍历两个列表，取出text, href, date
            data.append([m.attrib.get('title'), m.attrib.get('href'), ''.join(n).strip()])
            time.sleep(1) # 休眠一秒，防止反爬
    self.gov_data = data
    return data
```

同时在贵州省人民政府网下得出所有的[市(州)政府](https://www.guizhou.gov.cn/zwgk/zfxxgk/yqlj/szzf/)和[县(市、区、特区)政府](https://www.guizhou.gov.cn/zwgk/zfxxgk/yqlj/szzf/)的所有市州区县的名字，同样右键检查点击云岩区，lxml为：div>ul>li>a，编写代码：

```python
def get_gov_name(self, url:str, rule:str)->list:
    '''
    根据指定的url和指定的xpath规则
    :param url: 政府网址
    :param rule: xpath规则
    :return: 返回列表数据
    '''
    resp = requests.get(url=url)
    resp.encoding = resp.apparent_encoding
    html = etree.HTML(resp.text)
    return html.xpath(rule)
```

对于贵州省投资促进局，地方动态结构如下：

![image-20230412144402486](README.assets/image-20230412144402486.png)进行与贵州省人民政府地方动态相同逻辑，编写函数spider_invest()

### 4.2 数据库

拿到所有数据以后，需要保存到MYSQL里面，好处如下：

​	1.持久化保存数据

​	2.提供结构化查询语句

创建数据库gov，有两张表gov和location，分别记录市州区县的数据和市州区县的名字，且后者只保存名字，并不会在后面显示市、州、区、县等辖区字。gov的结构如下：

![image-20230412145408295](README.assets/image-20230412145408295.png)

其中，gov的建表语句为：

```sql
CREATE TABLE `gov` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL COMMENT '标题名称',
  `href` varchar(255) DEFAULT NULL COMMENT '新闻链接',
  `date` datetime DEFAULT NULL COMMENT '发布日期',
  `ref` varchar(255) NOT NULL COMMENT '所属地区',
  PRIMARY KEY (`id`),
  UNIQUE KEY `identification` (`href`) COMMENT '根据href来作为标识'
) ENGINE=InnoDB AUTO_INCREMENT=3497 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

- id为非空自增主键
- href为unique key

这里使用pymysql连接Python程序和MySQL数据库，pymysql是一个用于Python编程语言的MySQL客户端库，它允许开发者使用Python编写与MySQL数据库进行交互的应用程序。使用pymysql，开发者可以连接到MySQL服务器，执行查询和更新，处理结果集，并管理事务等。pymysql是一个开源库，可通过Python的包管理工具（如pip）轻松安装。

自定义useDBStore类，其中__init__函数可以完成相关配置，更换服务器只需更换连接参数(有默认值)即可，不用其他繁琐的步骤

```python
# 基本配置信息
def __init__(self, host='127.0.0.1', user='root', password='123456', database='gov', charset='utf8'):
    jieba.load_userdict('./mydict.txt') # 因为jieba不能识别两个地名，需要自定义词典
    self.host = host # 主机名
    self.user = user # 用户名
    self.password = password # 密码
    self.database = database # 连接的数据库
    self.charset = charset # 字符集
    self.db = pymysql.connect(host=self.host,user=self.user,password=self.password,database=self.database, charset=self.charset)
    # 拿到pymysql连接
```

首先将地域名全部保存到数据库里，编写函数keep_in_mysql2():

```python
def keep_in_mysql2(self, all_gov):
    '''
    按照贵州省人民政府网最新的地域规划，将所有区县保存到数据库里面
    :param all_gov: 所有市区县的名字
    :return:
    '''
    self.cursor = self.db.cursor()
    for i in range(0, len(all_gov)):
        # print(all_gov[i])
        sql = f"insert into location(location) values ('{all_gov[i]}');"
        # 运行sql语句
        self.cursor.execute(sql)
        # 修改
    self.db.commit()
    # 关闭游标
    self.cursor.close()
    # 关闭连接
    # print("victory!", type(self.cursor.fetchall()))
    # 关闭数据库连接
    self.db.close()
```

接着将爬取到的数千条政务数据保存到数据库里，采用Python的f-string拼接SQL语句，插入数据，编写函数keep_in_mysql():

```python
def keep_in_mysql(self, data:list):
    '''
    将从贵州省人民政府网和贵州省投资促进局爬取的数据保存到数据库
    :param data: 包含标题，链接，日期的二维列表
    :return:
    '''
    self.cursor = self.db.cursor()
    locations = self.location_mysql()
    # 将域名增加到ref字段
    for j in data:
        for i in locations.keys():
            if i in j[0]:
                j.append(i)
                break
        else:
            j.append(None)
    print(data)
    for i in range(0, len(data)):
        sql = f"insert into gov(title,href,date,ref) values ('{data[i][0]}','{data[i][1]}','{data[i][2]}','{data[i][3]}');"
        # 运行sql语句
        self.cursor.execute(sql)
        # 修改
    self.db.commit()
    # 关闭游标
    self.cursor.close()
    # 关闭连接
    # 关闭数据库连接
    self.db.close()
```

然后编写函数search_mysql()用于提供给外界查询符合要求的政务数据，参数TIME是"2020-04_2023-04"这样一个时间区间字符串，函数如下：

```python
def search_mysql(self, TIME)->tuple:
    '''
    根据时段字符串在数据库里面查询出来标题，链接
    :param TIME:包含开始日期和结束日期的时段
    :return:返回一个二维元组，第一维度是每一条数据，第二维度是每天数据有标题和链接两个属性
    '''
    self.cursor = self.db.cursor() # 获取游标
    begin, finish = TIME.split('_')[0], TIME.split('_')[1] # 切割时间字符串，得到起始，截止
    sql = f'select title, href, ref from gov where DATE_FORMAT(date,"%Y-%m") >="{begin}" and DATE_FORMAT(date,"%Y-%m")<="{finish}";'
    self.cursor.execute(sql) # 执行sql语句
    self.db.commit() # 提交到数据库
    return self.cursor.fetchall() # 返回查询结果
```

最后编写draw_cloud()生成词云图，编写函数：

```python
def draw_cloud(self, TIME):
    '''
    按照给定的时间字符串，查询数据库，计算词频，生成词云图
    :param TIME: 时间字符串，并且以此作为词云图名称
    :return: 字典，Key是地域名，Value是对应词频
    '''
    locations: tuple = self.location_mysql()
    text = self.jieba_process(self.search_mysql(TIME))
    print('text------------------------------>')
    print(text)
    for i in text:
        for j in locations.keys():
            if j in i:
                locations[j] += 1
                break
    print(locations)
    w1 = WordCloud(font_path=r'C:\Windows\Fonts\STXINWEI.TTF',
                   background_color='white', width=1600, height=800, collocations=False).generate_from_frequencies(locations)
    w1.to_file(f"{TIME}.png")
    self.cursor.close()
    return locations
```

### 4.3 交互式界面

展示效果如下：

![image-20230412152943992](README.assets/image-20230412152943992.png)

Python是一种非常流行的编程语言，有很多图形用户界面（GUI）框架可供选择。这里列出了几种流行的GUI框架及其特点和用途，供参考：

1. Tkinter： Tkinter是Python自带的GUI框架，适用于创建简单的GUI应用程序。它的特点是易于学习和使用，但在功能和外观方面有一定限制。
2. PyQt： PyQt是Python中的一个基于Qt库的GUI框架，适用于创建复杂的GUI应用程序。它具有丰富的特性和功能，可以创建跨平台的应用程序，但需要安装Qt库和PyQt模块。
3. wxPython： wxPython是一个基于wxWidgets库的Python GUI框架，它提供了跨平台的GUI开发工具包，可以创建本地的GUI应用程序。它的优点是易于学习和使用，并且具有丰富的GUI组件和特性。
4. PySide： PySide是一个基于Qt库的Python GUI框架，与PyQt类似，它也提供了Qt的所有特性和功能。它的优点是易于学习和使用，并且是开源的，但与PyQt不同的是，它的许可证更加宽松。
5. Kivy： Kivy是一个基于Python的开源GUI框架，专门用于创建跨平台的GUI应用程序。它的特点是易于学习和使用，可以创建多点触摸的应用程序，适用于移动设备和桌面应用程序。

因为本项目主要在后端数据爬取以及数据库逻辑，前端界面能够使用即可，因此采用Python自带的Tkinter模块。由上图可知，需要的控件有：

- Label widget，用于展示当前时间，可以编辑大小、颜色、方位和提示信息
- Combobox，用于提供下拉列表，其中每项的值要么是年份要么是月份，四个Combobox就可以组合成为"beginYear-beginMon_finishYear-finishMon"这样一个时间字符串交给后端数据库解析
- Button，文本为查询，当用户选择好下拉框之后再点击，就会向数据库发出查询
- TreeView，用于生成序号、标题、链接、区域这样一个表格，行数随着查询数据库返回的数据行数决定
- Scrollbar，因为表格可能过长，通过拉动滚动条来查看表格数据，而不是让表格无限制没有截止

GUI.py不仅承担了交互界面的构建，还是整个项目的入口文件，通过把项目按照功能划分为database，excel，interface，spider等模块，interface下的GUI.py作为程序主入口调动整个项目运行



贵州省大数据局是中国贵州省政府设立的机构，其主要职责是负责贵州省大数据战略规划和实施、推进贵州省大数据产业发展、建设贵州省大数据交易平台、提升贵州省大数据安全保障水平等。贵州省大数据局成立于2014年，是全国首个省级大数据管理机构。贵州省作为中国首个国家级大数据综合试验区，大力发展大数据产业，积极引导各类企业和机构来贵州发展大数据产业，促进贵州经济发展。大数据局的成立，对于推动贵州省大数据产业发展、提高贵州省数据治理水平具有重要意义。
本人在贵州省大数据局大数据产业发展中心数据资源管理处承担统筹数据资源建设和管理有关工作;统筹政务信息系统整合及数据共享开放，指导政务大数据、信息化重大项目建设方案编制;承担省级政务大数据、信息化建设方案审核;指导监督政府部门、重点行业的重要数据资源安全保障工作。主要负责和引导了一个政务数据爬虫系统--市州区县词频统计。在贵州省大数据局的实习中，我获得了实际操作和经验，掌握了大数据处理和分析的相关技能，了解了大数据行业的发展趋势和职业规划，同时也建立了职业人脉和提高了自己的沟通和协作能力，有了以下收获：
1.大数据分析和处理：使用数据挖掘、机器学习等技术，处理海量数据，提取有价值的信息和洞察。
2.数据建模和可视化：根据业务需求，设计数据模型，并将数据可视化，提供直观的数据展示和分析报告。
3.数据治理和安全：负责数据管理和保护，确保数据的完整性、安全性和隐私性。
4.业务分析和需求调研：与各业务部门沟通，了解业务需求，为业务提供数据支持和分析服务。
技术研究和创新：关注大数据领域最新技术和趋势，进行技术研究和创新，提高数据分析和处理效率和准确性。
学习到了以下技能和知识：
1.熟悉大数据分析和处理技术，如Hadoop、Spark、Python等。
2.具备良好的数据建模和可视化能力，熟练掌握数据建模工具和数据可视化工具。
3.了解数据安全和隐私保护的相关法律法规和标准，能够制定和实施相应的数据治理和安全策略。
4.具备较强的沟通能力和业务理解能力，能够与各业务部门进行有效的沟通和合作。
5.具备创新意识和技术研究能力，能够不断推动大数据领域的技术发展和创新。
作为贵州省大数据局的一员，我接触到最前沿的大数据技术和应用，同时也需要具备较强的技术和业务能力，不断提升自己，为数据驱动的业务提供更好的支持和服务。

![image-20230414113516836](README.assets/image-20230414113516836.png)

3. 系统技术
   1. 开发技术
   2. 框架设计
   3. 界面设计
   4. 数据库设计
4. 系统实现
   1. 项目概览
   2. 爬虫模块
   3. 数据库
   4. 交互式模块
5. 系统测试
   1. 测试目的
   2. 测试样例
6. 总结与展望
