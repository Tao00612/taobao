import re
import json
import time
import random
from retrying import retry
import spmpool
import requests
from taobao_login import UsernameLogin

# 关闭警告
requests.packages.urllib3.disable_warnings()


class GoodsSpider:

    def __init__(self, q):
        self.q = q
        # 超时
        self.timeout = 15
        self.goods_list = []

        # 添加连接池配置
        spmpool.add_config('local', 'root', '123', 'spidernew', init_pool_size=20)
        # 获取连接池
        local_pool = spmpool.spmpool('local')
        # 获取连接并使用
        self.conn = local_pool.get()

        # 登录淘宝
        tbl = UsernameLogin(session)
        tbl.login()

    @retry(stop_max_attempt_number=3)
    def spider_goods(self, page):
        """

        :param page: 淘宝分页参数
        :return:
        """
        s_num = page * 44
        # 搜索链接，q参数表示搜索关键字，s=page*44 数据开始索引
        search_url = f'https://s.taobao.com/search?q={self.q}&sort=sale-desc&s={s_num}'
        # 代理ip，网上搜一个，猪哥使用的是 站大爷：http://ip.zdaye.com/dayProxy.html
        # 尽量使用最新的，可能某些ip不能使用，多试几个。后期可以考虑做一个ip池
        proxies = {
                   'https': '114.116.75.60:18190'
                   }
        user_agent_list = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
            "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 "
            "(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 "
            "(KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 "
            "(KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 "
            "(KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 "
            "(KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 "
            "(KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
            "(KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 "
            "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 "
            "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        ]
        ua = random.choice(user_agent_list)
        # 请求头
        headers = {
            'referer': 'https://www.taobao.com/',
            'User-Agent': ua
        }
        response = session.get(search_url, headers=headers,
                               verify=False, timeout=self.timeout)
        goods_match = re.search(r'g_page_config = (.*?)}};', response.text)
        # 没有匹配到数据
        if not goods_match:
            print('提取页面中的数据失败！')
            # print(response.text)
            with open('tb.html','w',encoding='utf-8') as f:
                f.write(response.text)
            raise RuntimeError
        goods_str = goods_match.group(1) + '}}'
        goods_list = self._get_goods_info(goods_str)
        self._save_mysql(goods_list)
        # print(goods_str)

    def _get_goods_info(self, goods_str):
        """
        解析json数据，并提取标题、价格、商家地址、销量、评价地址
        :param goods_str: string格式数据
        :return:
        """
        goods_json = json.loads(goods_str)
        goods_items = goods_json['mods']['itemlist']['data']['auctions']
        goods_list = []
        for goods_item in goods_items:
            goods = {'title': goods_item['raw_title'],
                     'price': goods_item['view_price'],
                     'location': goods_item['item_loc'],
                     'sales': goods_item['view_sales'],
                     'comment_url': goods_item['comment_url'],
                     'nick': goods_item['nick']
                     }
            goods_list.append(goods)
        return goods_list

    # def _save_excel(self, goods_list):
    #     """
    #     将json数据生成excel文件
    #     :param goods_list: 商品数据
    #     :param startrow: 数据写入开始行
    #     :return:
    #     """
    #     # pandas没有对excel没有追加模式，只能先读后写
    #     if os.path.exists(GOODS_EXCEL_PATH):
    #         df = pd.read_excel(GOODS_EXCEL_PATH)
    #         df = df.append(goods_list)
    #     else:
    #         df = pd.DataFrame(goods_list)
    #
    #     writer = pd.ExcelWriter(GOODS_EXCEL_PATH)
    #     # columns参数用于指定生成的excel中列的顺序
    #     df.to_excel(excel_writer=writer, columns=['title', 'price', 'location', 'sales', 'comment_url'], index=False,
    #                 encoding='utf-8', sheet_name='Sheet')
    #     writer.save()
    #     writer.close()

    def _save_mysql(self, items):
        # fields = ','.join(item.keys())
        # value = ','.join(['%%(%s)s' % key for key in item])
        sql = """
            insert into tb_product(%s) values(%s)
        """
        for item in items:
            fields = ','.join(item.keys())
            value = ','.join(['%%(%s)s' % key for key in item])
            try:
                self.conn.execute(sql % (fields, value), item)
                print('已保存数据库------')
            except Exception as e:
                print(e)
                self.conn.rollback()

    def _save_mysql_me(self, item):
        sql = """
            insert into tb_me(%s) values(%s)
        """
        fields = ','.join(item.keys())
        value = ','.join(['%%(%s)s' % key for key in item])
        try:
            self.conn.execute(sql % (fields, value), item)
            print('已保存数据库------')
        except Exception as e:
            print(e)
            self.conn.rollback()

    def patch_spider_goods(self):
        """
        批量爬取淘宝商品
        如果爬取20多页不能爬，可以分段爬取
        :return:
        """
        # 写入数据前先清空之前的数据
        # if os.path.exists(GOODS_EXCEL_PATH):
        #     os.remove(GOODS_EXCEL_PATH)
        # 批量爬取，自己尝试时建议先爬取3页试试
        for i in range(0, 1):
            print('第%d页' % (i + 1))
            self.spider_goods(i)
            # 设置一个时间间隔
            time.sleep(random.randint(10, 15))

    def get_me_product(self):
        my_url = "https://buyertrade.taobao.com/trade/itemlist/list_bought_items.htm"
        proxies = {'http': '114.116.75.60:18190',
                   'https': '119.3.37.101:5481'
                   }
        headers = {
            'referer': 'https://www.taobao.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = session.get(my_url, headers=headers, proxies=proxies,
                               verify=False, timeout=self.timeout)
        response.encoding = 'unicode_escape'
        result = re.findall(r"var data = JSON\.parse\('(.*?)'\);", response.text)
        if result:
            json_data = json.loads(result[0])
            product_list = json_data['mainOrders']
            for product in product_list:
                item = {}
                item['name'] = product['subOrders'][0]['itemInfo']['title']
                item['price'] = product['payInfo']['actualFee']
                item['status'] = product['statusInfo']['text']
                self._save_mysql_me(item)
        else:
            print('没有数据')


if __name__ == '__main__':
    session = requests.session()
    gs = GoodsSpider('内衣')
    # gs.patch_spider_goods()
    # gs.get_me_product()
