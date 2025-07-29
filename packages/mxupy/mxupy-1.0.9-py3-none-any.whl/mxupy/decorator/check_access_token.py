from mxupy import get_method

def check_access_token(func):
    """ 校验访问令牌

    Args:
        func (method): 函数
    """
    def _do(*args, **kwargs):
        
        at = kwargs.get('access_token')
        uid = kwargs.get('user_id')
        
        # 校验令牌
        method = get_method('liveheroes.UserControl.check_accesstoken')
        im = method(**{'userId':uid, 'accesstoken':at})
        if im.error:
            return im
        
        # 执行函数
        result = func(*args, **kwargs)
        return result
    
    return _do