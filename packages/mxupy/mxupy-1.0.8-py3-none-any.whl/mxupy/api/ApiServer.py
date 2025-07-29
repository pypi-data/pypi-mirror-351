import json
import os
import ast
import asyncio
import uvicorn
import platform

import numpy as np
import mxupy as mu

from peewee import Model
from datetime import datetime
from playhouse.shortcuts import model_to_dict
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Optional,Any
from fastapi import FastAPI, HTTPException, Response, Request, UploadFile, File, Form, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from pydantic import BaseModel, Field

from mxupy import IM, get_method, read_config, get_attr


class RequestTimerMiddleware(BaseHTTPMiddleware):
    """ 打印访问开始时间和结束时间，以及访问时长

    Args:
        BaseHTTPMiddleware (StreamingResponse): 响应流
    """

    async def dispatch(self, request: Request, call_next):

        st = datetime.now()
        response = await call_next(request)
        et = datetime.now()

        # 调用信息
        start_time_str = str(st)[:-3]
        end_time_str = str(et)[:-3]
        duration_str = str(et - st)[:-3]
        status_code_str = str(response.status_code)
        url_str = str(request.url)
        method_str = str(request.method)
        path_params_str = str(request.path_params)
        query_params_str = str(request.query_params)

        access_info = f'access_info:: start: {start_time_str} end: {end_time_str} duration: {duration_str}ms ' \
                      f'status_code: {status_code_str} url: {url_str} method: {method_str} ' \
                      f'path_params: {path_params_str} query_params: {query_params_str}'

        print(access_info)

        return response


class ApiServer:
    """ 配置服务器信息，并开启服务，通过 api 路由执行底层函数
    """

    def __init__(self):

        # 读取配置信息
        api_server = read_config().get('api_server', {})

        # 域名、端口、ssl 证书
        self.host = api_server.get('host', '0.0.0.0')
        self.port = int(api_server.get('port', '80'))
        self.ssl_keyfile = api_server.get('ssl_keyfile', '')
        self.ssl_certfile = api_server.get('ssl_certfile', '')

        # 是否允许浏览器发送凭证信息（如 cookies）到服务器
        # 这里可以指定允许访问的源，可以是具体的域名或 '*'（表示允许所有源）
        # 允许的 HTTP 方法，例如 'GET', 'POST', 'PUT', 'DELETE', 等
        # 允许的 HTTP 头部信息
        self.allow_credentials = api_server.get('allow_credentials', True)
        self.allow_origins = api_server.get('allow_origins', ['*'])
        self.allow_methods = api_server.get('allow_methods', ['*'])
        self.allow_headers = api_server.get('allow_headers', ['*'])

        # 配置 CORS 中间件
        self.app = FastAPI()
        self.app.add_middleware(
            CORSMiddleware,
            allow_credentials=self.allow_credentials,
            allow_origins=self.allow_origins,
            allow_methods=self.allow_methods,
            allow_headers=self.allow_headers,
        )

        # 调试模式会打印访问的时间等信息
        self.debug = api_server.get('debug', True)

        # 文件缓存时长，单位（秒）
        self.access_file_max_age = api_server.get('access_file_max_age', 31536000)
        self.headers = {
            'Cache-Control': 'max-age=' + str(self.access_file_max_age)
        }

    def handle_data(self, result):
        """ 处理函数返回的结果，转成字典让前端以 json 形式接收
            # [1] 结果类
            # [2] 数组
            # [3] 简单类型
        Args:
            result (any): 执行函数后返回的结果
        """

        im = IM()

        # [1] 结果类
        if isinstance(result, IM):

            # 将结果类中的数据 to_dict
            if isinstance(result.data, Model):
                result.data = model_to_dict(result.data, False)
            elif isinstance(result.data, list):
                datas = []
                for data in result.data:
                    datas.append(model_to_dict(data, False) if isinstance(data, Model) else data)
                result.data = datas

            # 将结果类 to_dict
            im = result.model_dump()

        else:
            # [2] 数组、[3] 简单类型
            im.data = result.tolist() if isinstance(result, np.ndarray) else result

        return im

    def call(self, name, params) -> IM:
        """ 通过 函数名 和 参数集 访问 函数

        Args:
            name (str): 函数名
            params (obj): 参数集

        Returns:
            IM: 结果类
        """
        im = IM(True, 'success')

        if not name:
            return IM(True, 'Module or function cannot be empty.')

        try:
            # [1] 获取函数
            method = get_method(name)
            if not method:
                im = IM(False, "Module or function not found.", code=404)
                print(im)
                return im

            # [2] 调用函数
            result = method(**params) if params else method()

            # [3] 处理结果
            im = self.handle_data(result)
        except Exception as e:
            im = IM(False, f"An error occurred: {e}, {mu.getErrorStackTrace()}")
            print(im)
            return im

        return im

    def call_for_bcpost(self, params: dict) -> IM:
        """ 根据前端传过来的函数信息，执行相应的函数
            分 3 步：[1] 获取函数、[2] 执行函数、[3] 处理函数返回结果

        Args:
            info (ApiInfo): 函数信息

        Returns:
            IM: 结果类
        """
        # 函数名、令牌
        name = get_attr(params, '___functionName')
        token = get_attr(params, '___accessToken')

        # 参数，将字典参数转为对象
        ps = {}
        for k, v in params.items():
            if not k.startswith('___'):
                ps[k] = v

        if self.debug:
            print('api_info:: ' + name + ' ' + str(ps))

        obj = mu.param_to_obj(ps)
        return self.call(name, obj)

    def call_for_get(self, name: str, params: str = None) -> IM:
        """ 根据前端传过来的函数信息，执行相应的函数
            分 3 步：[1] 获取函数、[2] 执行函数、[3] 处理函数返回结果

        Args:
            info (ApiInfo): 函数信息

        Returns:
            IM: 结果类
        """
        if self.debug:
            print('api_info:: ' + name + ' ' + str(params))

        # 参数
        ps = None
        obj = None
        if params:
            # 将字符串转为对象
            ps = params.replace("{", '{"').replace(":", '":').replace(",", ',"')
            ps = ast.literal_eval(ps)
            obj = mu.param_to_obj(ps)

        return self.call(name, obj)

    def call_for_post(self, name:str=Form(...), params: str = Form(None)) -> IM:
        """ 根据前端传过来的函数信息，执行相应的函数
            分 3 步：[1] 获取函数、[2] 执行函数、[3] 处理函数返回结果

        Args:
            info (ApiInfo): 函数信息

        Returns:
            IM: 结果类
        """
        # 参数，将字典参数转为对象
        ps = {}
        params_dict = json.loads(params)
        for k, v in params_dict.items():
            ps[k] = v

        obj = mu.param_to_obj(ps)
        return self.call(name, obj)

    # 读取文件/上传文件
    def read_file(self, filename:str, type:str='user', userId:int = -1, sub_dir:str = '', download:bool=False) -> FileResponse:
        return mu.read_file(filename, type, userId, sub_dir, download)
    def upload_file(self, file:UploadFile = File(...), keep:bool = Form(True), override:bool = Form(False), sub_dir:str = Form(''), 
                    *, chunk_index:int = Form(-1), total_chunks:int = Form(1), 
                    userId:int = Form(...), access_token:str = Form(...)) -> IM:
        return mu.upload_user_file(file, keep, override, sub_dir, chunk_index=chunk_index, total_chunks=total_chunks, 
                    user_id=userId, access_token=access_token)

    def run(self, startupHandler=None, shutdownHandler=None):
        """ 运行 FastAPI
        """
        # 在 Windows 上，asyncio 需要使用特定的事件循环策略来处理套接字操作，
        # 否则可能会遇到 ConnectionResetError: [WinError 10054] 这样的错误
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        # 打印日志
        if self.debug:
            self.app.add_middleware(RequestTimerMiddleware)

        if startupHandler is not None:
            self.app.add_event_handler("startup", startupHandler)

        if shutdownHandler is not None:
            self.app.add_event_handler("shutdown", shutdownHandler)

        # 添加路由
        self.app.get('/api', response_model=IM)(self.call_for_get)
        self.app.post('/api', response_model=IM)(self.call_for_post)
        self.app.post('/bcapi', response_model=IM)(self.call_for_bcpost)
        self.app.get('/file', response_model=None)(self.read_file)
        self.app.post('/file', response_model=IM)(self.upload_file)

        uvicorn.run(self.app, host=self.host, port=self.port, ssl_certfile=self.ssl_certfile, ssl_keyfile=self.ssl_keyfile)


if __name__ == '__main__':
    ApiServer().run()
