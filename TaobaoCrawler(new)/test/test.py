import spmpool

# 添加连接池配置
spmpool.add_config('local', 'root', '123', 'spidernew', init_pool_size=20)
# spmpool.add_config('remote', 'ujued', '123456', 'db', init_pool_size=120)

# 获取连接池
local_pool = spmpool.spmpool('local')
# remote_pool = spmpool.spmpool('remote')

sql = """
 insert into tb_product(title,price,location,sales,comment_url,nick,comment_count) values(%(title)s,%(price)s,%(location)s,%(sales)s,%(comment_url)s,%(nick)s,%(comment_count)s)
"""
item ={'title': '知味观绿豆糕杭州特产桂花绿豆饼糕点小礼盒老式传统美食抹茶零食', 'price': '19.90', 'location': '浙江 杭州', 'sales': '8500+人收货', 'comment_url': '//detail.tmall.com/item.htm?id=546290130158&ns=1&abbucket=13&on_comment=1', 'nick': '知味观官方旗舰店', 'comment_count': '129132'}
# 获取连接并使用

conn = local_pool.get()
conn.execute(sql,item)

conn.close()

# # 导入pymysql模块
# import pymysql
#
# # 连接database
# conn = pymysql.connect(
#     host='127.0.0.1',
# user ='root', password ='123',
# database ='spidernew',
# charset ='utf8')
#
# # 得到一个可以执行SQL语句的光标对象
# cursor = conn.cursor()  # 执行完毕返回的结果集默认以元组显示
# # 得到一个可以执行SQL语句并且将结果作为字典返回的游标
# # cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
#
# # 定义要执行的SQL语句
# sql = """
#  insert into tb_product(title,price,location,sales,comment_url,nick,comment_count) values(%(title)s,%(price)s,%(location)s,%(sales)s,%(comment_url)s,%(nick)s,%(comment_count)s)
# """
# item ={'title': '知味观绿豆糕杭州特产桂花绿豆饼糕点小礼盒老式传统美食抹茶零食', 'price': '19.90', 'location': '浙江 杭州', 'sales': '8500+人收货', 'comment_url': '//detail.tmall.com/item.htm?id=546290130158&ns=1&abbucket=13&on_comment=1', 'nick': '知味观官方旗舰店', 'comment_count': '129132'}
#
# # 执行SQL语句
# cursor.execute(sql,item)
#
# conn.commit()
# # 关闭光标对象
# cursor.close()
#
# # 关闭数据库连接
# conn.close()

