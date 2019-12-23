container_id = 'https://m.weibo.cn/api/container/getSecond?containerid=1005051647486362_-_FANS'

def get_container_id(s):
    import re
    return re.findall('[0-9]\d*',s)[0]

print(get_container_id(container_id))