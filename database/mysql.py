import pymysql
import jieba
from wordcloud import WordCloud

class useDBStore:

    def __init__(self, host='127.0.0.1', user='root', password='123456', database='gov', charset='utf8'):
        jieba.load_userdict('./mydict.txt')
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset
        self.db = pymysql.connect(host=self.host,user=self.user,password=self.password,database=self.database, charset=self.charset)


    def keep_in_mysql(self, data:list):
        '''
        将从贵州省人民政府网和贵州省投资促进局爬取的数据保存到数据库
        :param data: 包含标题，链接，日期的二维列表
        :return:
        '''
        self.cursor = self.db.cursor()
        for i in range(0, len(data)):
            print(str(data[i][0]), data[i][1], str(data[i][2]))
            sql = f"insert into gov(title,href,date) values ('{data[i][0]}','{data[i][1]}','{data[i][2]}');"

            # 运行sql语句
            self.cursor.execute(sql)
            # 修改
        self.db.commit()
        # 关闭游标
        self.cursor.close()
        # 关闭连接
        print("victory!", self.cursor.fetchall())
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
            print(all_gov[i])
            sql = f"insert into location(location) values ('{all_gov[i]}');"

            # 运行sql语句
            self.cursor.execute(sql)
            # 修改
        self.db.commit()
        # 关闭游标
        self.cursor.close()
        # 关闭连接
        print("victory!", type(self.cursor.fetchall()))
        # 关闭数据库连接
        self.db.close()

    def search_mysql(self, TIME)->tuple:
        '''
        根据时段字符串在数据库里面查询出来标题，链接
        :param TIME:包含开始日期和结束日期的时段
        :return:返回一个二维元组，第一维度是每一条数据，第二维度是每天数据有标题和链接两个属性
        '''
        self.cursor = self.db.cursor()
        begin, finish = TIME.split('_')[0], TIME.split('_')[1]
        sql = f'select title, href from gov where DATE_FORMAT(date,"%Y-%m") >="{begin}" and DATE_FORMAT(date,"%Y-%m")<="{finish}";'
        self.cursor.execute(sql)
        self.db.commit()
        return self.cursor.fetchall()

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
        将数据经过jieba分词
        :param searchMysql: search_mysql()的返回值
        :return:
        '''
        text = ''
        for i in searchMysql:
            text += i[0]

        return jieba.lcut(text)

    def draw_cloud(self, TIME):
        locations: tuple = self.location_mysql()
        text = self.jieba_process(self.search_mysql(TIME))
        for i in text:
            for j in locations.keys():
                if j in i:
                    locations[j] += 1
        t = ''
        for i in locations:
            i *= locations[i]
            t += i
        print(' '.join(jieba.lcut(t)))
        w1 = WordCloud(font_path=r'C:\Windows\Fonts\STXINWEI.TTF',
                       background_color='white', width=1600, height=800, collocations=False).generate(
            ' '.join(jieba.lcut(t)))
        w1.to_file(f"{TIME}.png")
        self.cursor.close()
    def update_gov(self, data):
        pass

db = useDBStore()
# db.draw_cloud('2023-01_2023-02')
print(';;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;')
print(db.location_mysql())