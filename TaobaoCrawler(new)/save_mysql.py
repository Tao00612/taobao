from config import *
import spmpool

# 添加连接池配置
spmpool.add_config('local', 'root', '123', 'spidernew', init_pool_size=20)

# 获取连接池
local_pool = spmpool.spmpool('local')
conn = local_pool.get()


def save_mysql(res_list):
    for i in res_list:
        item = {}
        item['title'] = i['title']
        item['price'] = i['promoPrice'] if i['promoPrice'] else i['price']
        item['location'] = i['loc']
        item['sales'] = i['sellCount']
        item['comment_url'] = i['eurl']
        item['nick'] = i['wangwangId']
        _save_mysql(item)


def _save_mysql(item):
    sql = """
        insert into tb_product(%s) values(%s)
    """
    fields = ','.join(item.keys())
    value = ','.join(['%%(%s)s' % key for key in item])
    try:
        conn.execute(sql % (fields, value), item)
    except Exception as e:
        print(e)
        conn.rollback()
