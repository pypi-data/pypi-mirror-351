import types

def str_to_dict(src):
    """ 将查询字符串转换成字典

    Returns:
        dict: 字典
    """
    # 原始字符串
    # s = "a=1&b=2&c=3"
    src = str(src)
    if src.startswith('?'):
        src = src[1:]

    # 将字符串分割成键值对
    pairs = src.split("&")
    # 创建字典
    dic = {}
    for pair in pairs:
        # 分割键和值
        key, value = pair.split("=")
        # 将键和值添加到字典中
        dic[key] = value
        
    return dic

def str_to_obj(src):
    """ 将查询字符串转换成字典

    Returns:
        dict: 字典
    """
    dic = str_to_dict(src)

    # 将字典转换为对象
    obj = types.SimpleNamespace(**dic)
    return obj