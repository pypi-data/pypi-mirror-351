"""杂鱼♡～这是本喵为你写的dataclass到JSON的序列化函数喵～才不是特意为了杂鱼写的呢～"""

import os
import json
import datetime
import uuid
import tempfile
from decimal import Decimal
from typing import Any
from dataclasses import is_dataclass
from pydantic import BaseModel

from .core import T, convert_dataclass_to_dict
from .file_ops import ensure_directory_exists

# 杂鱼♡～本喵创建了一个自定义JSON编码器，这样就可以处理各种复杂类型喵～
class JSDCJSONEncoder(json.JSONEncoder):
    """杂鱼♡～这是本喵为你特制的JSON编码器喵～可以处理各种特殊类型哦～"""
    
    def default(self, obj: Any) -> Any:
        """杂鱼♡～本喵会把这些特殊类型转换成JSON兼容的格式喵～"""
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.time):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return obj.total_seconds()
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        elif isinstance(obj, Decimal):
            return str(obj)
        elif isinstance(obj, set):
            return list(obj)
        elif is_dataclass(obj):
            return convert_dataclass_to_dict(obj)
        # 杂鱼♡～其他类型就交给父类处理喵～
        return super().default(obj)

def jsdc_dumps(obj: T, indent: int = 4) -> str:
    """杂鱼♡～本喵帮你把dataclass或Pydantic模型实例序列化成JSON字符串喵～

    这个函数接收一个dataclass实例，并将其序列化为JSON字符串喵～
    JSON输出可以使用指定的缩进级别格式化喵～杂鱼是不是太懒了，连文件都不想写呢♡～

    Args:
        obj (T): 要序列化的dataclass实例喵～
        indent (int, optional): JSON输出中使用的缩进空格数喵～默认是4～看起来整齐一点～

    Returns:
        str: 序列化后的JSON字符串喵～杂鱼可以好好利用它哦～

    Raises:
        TypeError: 如果obj不是dataclass或BaseModel，杂鱼肯定传错参数了～
        ValueError: 如果序列化过程中出错，本喵会生气地抛出错误喵！～
    """
    if indent < 0:
        raise ValueError("杂鱼♡～缩进必须是非负数喵！～负数是什么意思啦～")

    try:
        if isinstance(obj, type):
            raise TypeError("杂鱼♡～obj必须是实例而不是类喵！～你真是搞不清楚呢～")
            
        if not (is_dataclass(obj) or isinstance(obj, BaseModel)):
            raise TypeError('杂鱼♡～obj必须是dataclass或Pydantic BaseModel实例喵！～')
            
        # 获取对象的类型提示
        obj_type = type(obj)
        
        # 杂鱼♡～本喵把类型信息也传递给转换函数，这样就能进行完整的类型验证了喵～
        data_dict = convert_dataclass_to_dict(obj, parent_key="root", parent_type=obj_type)
        return json.dumps(data_dict, ensure_ascii=False, indent=indent, cls=JSDCJSONEncoder)
    except TypeError as e:
        raise TypeError(f"杂鱼♡～类型验证失败喵：{str(e)}～真是个笨蛋呢～")
    except Exception as e:
        raise ValueError(f"杂鱼♡～序列化过程中出错喵：{str(e)}～")

def jsdc_dump(obj: T, output_path: str, encoding: str = 'utf-8', indent: int = 4) -> None:
    """杂鱼♡～本喵帮你把dataclass或Pydantic模型实例序列化成JSON文件喵～

    这个函数接收一个dataclass实例，并将其序列化表示写入到指定文件中，
    格式为JSON喵～输出文件可以使用指定的字符编码，JSON输出可以
    使用指定的缩进级别格式化喵～杂鱼一定会感激本喵的帮助的吧♡～
    
    本喵会使用临时文件进行安全写入，防止在写入过程中出错导致文件损坏喵～

    Args:
        obj (T): 要序列化的dataclass实例喵～
        output_path (str): 要保存JSON数据的输出文件路径喵～杂鱼可别搞错路径哦～
        encoding (str, optional): 输出文件使用的字符编码喵～默认是'utf-8'～
        indent (int, optional): JSON输出中使用的缩进空格数喵～默认是4～看起来整齐一点～

    Raises:
        ValueError: 如果提供的对象不是dataclass或路径无效，本喵会生气地抛出错误喵！～
        TypeError: 如果obj不是dataclass或BaseModel，杂鱼肯定传错参数了～
        OSError: 如果遇到文件系统相关错误，杂鱼的硬盘可能有问题喵～
        UnicodeEncodeError: 如果编码失败，杂鱼选的编码有问题喵！～
    """
    if not output_path or not isinstance(output_path, str):
        raise ValueError("杂鱼♡～输出路径无效喵！～")
    
    if indent < 0:
        raise ValueError("杂鱼♡～缩进必须是非负数喵！～负数是什么意思啦～")

    # 获取输出文件的绝对路径喵～
    abs_output_path = os.path.abspath(output_path)
    directory = os.path.dirname(abs_output_path)
    
    try:
        # 确保目录存在且可写喵～
        ensure_directory_exists(directory)

        if isinstance(obj, type):
            raise TypeError("杂鱼♡～obj必须是实例而不是类喵！～你真是搞不清楚呢～")
            
        if not (is_dataclass(obj) or isinstance(obj, BaseModel)):
            raise TypeError('杂鱼♡～obj必须是dataclass或Pydantic BaseModel实例喵！～')
            
        # 杂鱼♡～先序列化为字符串喵～
        json_str = jsdc_dumps(obj, indent)
        
        # 杂鱼♡～使用临时文件进行安全写入喵～
        # 在同一目录创建临时文件，确保重命名操作在同一文件系统内执行喵～
        temp_file = tempfile.NamedTemporaryFile(
            prefix=f'.{os.path.basename(abs_output_path)}.', 
            dir=directory, 
            suffix='.tmp',
            delete=False,
            mode='w',
            encoding=encoding
        )
        
        temp_path = temp_file.name
        try:
            # 杂鱼♡～写入临时文件喵～
            temp_file.write(json_str)
            # 必须先刷新缓冲区喵～
            temp_file.flush()
            # 确保文件内容已完全写入磁盘喵～然后再关闭文件～
            os.fsync(temp_file.fileno())
            temp_file.close()
                
            # 杂鱼♡～使用原子操作将临时文件重命名为目标文件喵～
            # 在Windows上，如果目标文件已存在，可能会失败，所以先尝试删除喵～
            if os.path.exists(abs_output_path):
                os.remove(abs_output_path)
                
            # 杂鱼♡～安全地重命名文件喵～
            os.rename(temp_path, abs_output_path)
        except Exception as e:
            # 杂鱼♡～如果出错，清理临时文件喵～
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass  # 杂鱼♡～如果连临时文件都删不掉，本喵也无能为力了喵～
            raise e  # 杂鱼♡～重新抛出原始异常喵～
            
    except OSError as e:
        raise OSError(f"杂鱼♡～创建目录或访问文件失败喵：{str(e)}～")
    except TypeError as e:
        raise TypeError(f"杂鱼♡～类型验证失败喵：{str(e)}～真是个笨蛋呢～")
    except Exception as e:
        raise ValueError(f"杂鱼♡～序列化过程中出错喵：{str(e)}～") 