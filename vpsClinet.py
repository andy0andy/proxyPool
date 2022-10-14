import random



"""
vps相关管理
1. 自动拨号
2. 拨号控频
3. 获取代理
"""

class VpsClient(object):

    def get_proxy(self):
        return f"{random.randint(0, 256)}.{random.randint(0, 256)}.{random.randint(0, 256)}.{random.randint(0, 256)}:{random.randint(111, 10000)}"




if __name__ == '__main__':
    proxy = VpsClient().get_proxy()
    print(proxy)




