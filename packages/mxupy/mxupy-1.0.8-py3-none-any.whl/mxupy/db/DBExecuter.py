import json
import traceback
from peewee import *
from playhouse.shortcuts import model_to_dict
from mxupy import IM

class DBExecuter:

    def __init__(self, db):
        """ 初始化

        Args:
            db (obj): 模型所在数据库
        """
        self.db = db

    def run(self, operation):
        """ 执行数据库操作，分为3步：
            1、开始一个事务
            2、执行数据库操作
            3、提交事务

        Args:
            operation (func): 操作

        Returns:
            im: 执行结果
        """
        im = IM()
        try:
            # 开始一个事务、执行数据库操作、提交事务
            self.db.begin()
            operation(im)
            self.db.commit()
            
        except IntegrityError as e:
            im.success = False
            im.msg = f"dbBigOAINET IntegrityError: {e}"
            im.error = 'IntegrityError'
            print(im.msg)
            traceback.print_exc()
            self.db.rollback()
            
        except DatabaseError as e:
            im.success = False
            im.msg = f"dbBigOAINET DatabaseError: {e}"
            im.error = 'DatabaseError'
            print(im.msg)
            traceback.print_exc()
            self.db.rollback()
            
        except OperationalError as e:
            im.success = False
            im.msg = f"dbBigOAINET OperationalError: {e}"
            im.error = 'OperationalError'
            print(im.msg)
            traceback.print_exc()
            self.db.rollback()
            
        except DoesNotExist as e:
            im.success = False
            im.msg = f"dbBigOAINET DoesNotExist: {e}"
            im.error = 'DoesNotExist'
            print(im.msg)
            traceback.print_exc()
            self.db.rollback()
            
        except Exception as e:
            im.success = False
            im.msg = f"dbBigOAINET An unexpected error occurred: {e}"
            im.error = 'Exception'
            print(im.msg)
            traceback.print_exc()
            self.db.rollback()

        return im

    def to_model(self, model, clazz):
        """ 转为模型

        Args:
            model (model): 模型
            clazz (type): 类型

        Returns:
            model: 模型
        """
        im = IM()
        try:
            if isinstance(model, str):
                model = json.loads(model)

            if isinstance(model, dict):
                model = clazz(**model)

            im.data = model
        except Exception as e:
            im.success = False
            im.msg = f"dbBigOAINET to_model error occurred: {e}"
            im.error = 'Exception'
            print(im.msg)
            traceback.print_exc()

        return im

    def to_dict(self, model):
        """ 将模型转为字典

        Args:
            model (model): 模型

        Returns:
            dict: 字典
        """
        im = IM()
        try:
            if isinstance(model, str):
                model = json.loads(model)

            if isinstance(model, Model):
                # model_dict = {}
                # for field in model.dirty_fields:
                #     value = getattr(model, field.name)
                #     if isinstance(field, ForeignKeyField) and value is not None:
                #         # 对于外键字段，使用字段名加上 'Id' 作为键
                #         model_dict[field.name + 'Id'] = value
                #     else:
                #         # 对于非外键字段，直接使用字段名作为键
                #         model_dict[field.name] = value
                #         # model_dict[field.name] = model_to_dict(value, recurse=False, backrefs=False)
                # model = model_dict
                model = model_to_dict(model, recurse=False, backrefs=False)

            im.data = model
        except Exception as e:
            im.success = False
            im.msg = f"dbBigOAINET to_dict error occurred: {e}"
            im.error = 'Exception'
            print(im.msg)
            traceback.print_exc()

        return im

        """ 
            返回给定模型类的主键字段名称。
        Args:
            model_class (class): 继承自 peewee.Model 的类。

        Returns:
            str: 主键字段的名称
        """
        # 获取模型类的元数据
        meta = model_class._meta
        # 检查主键字段
        primary_key_field = meta.primary_key
        # 返回主键字段的名称
        return primary_key_field.name
