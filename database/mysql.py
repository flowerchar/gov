import pymysql
import jieba
from wordcloud import WordCloud
from spider.govspider import GovSpider
class useDBStore:
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

    def location_mysql(self) -> dict:
        '''
        从数据库里面查询市区县地域的名称
        :return: 一个Key为地名，初始value全为0的字典
        '''
        self.cursor = self.db.cursor()
        sql = 'SELECT location FROM location;'
        self.cursor.execute(sql)
        self.db.commit()

        words = []
        for i in self.cursor.fetchall():
            words.append(i[0])
        return dict(zip(words, [0 for i in range(0, len(words))]))

    def jieba_process(self, searchMysql:tuple):
        '''
        将标题经过jieba分词
        :param searchMysql: search_mysql()的返回值
        :return: 返回值是一个列表，里面是将标题分词，并且将每一个标题的分词加到这个列表里面
        '''
        text = ''
        for i in searchMysql:
            text += i[0]

        return jieba.lcut(text)

    # def keep_in_mysql_ref(self, ref):
    #     self.cursor = self.db.cursor()
    #     for i in range(0, len(ref)):
    #         sql = f"insert into gov(ref) values ('{ref[i]}');"
    #         # 运行sql语句
    #         self.cursor.execute(sql)
    #         # 修改
    #
    #     self.db.commit()
    #     self.cursor.close()

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

    def update_gov(self, data):
        pass

if __name__ == '__main__':

    db = useDBStore()
    g = GovSpider().spider_gov()
    print(g)
    db.keep_in_mysql(g)