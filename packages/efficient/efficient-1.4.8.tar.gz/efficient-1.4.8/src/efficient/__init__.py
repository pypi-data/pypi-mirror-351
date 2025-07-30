import sys
import subprocess
from time import time_ns


def call_timer(func):
    def wrapper(*args, **kwargs):
        t = time_ns()
        r = func(*args, **kwargs)
        print(func.__name__, '执行用时', (time_ns() - t) / 1000000000, f"{func.__code__.co_filename}, line {func.__code__.co_firstlineno + 1}")
        return r

    return wrapper


# print的颜色
def color(content, conf='0'):
    """
    格式：\033[显示方式;前景色;背景色m … \033[0m
    显示方式，前景色，背景色是可选参数，可以只写其中的某一个或者某两个；
    由于表示三个参数不同含义的数值都是唯一没有重复的，所以三个参数的书写先后顺序没有固定要求，系统都可识别；
    建议按照默认的格式规范书写。
    # 显示方式
    0	终端默认设置
    1	高亮显示
    4	使用下划线
    5	闪烁
    7	反白显示
    8	不可见
    22	非高亮显示
    24	去下划线
    25	去闪烁
    27	非反白显示
    28	可见
    # 前景色/背景色
    30	40	黑色
    31	41	红色
    32	42	绿色
    33	43	黄色
    34	44	蓝色
    35	45	紫红色
    36	46	青蓝色
    37	47	白色
    # 示例
    print(color('红字白底', '4;31;47'))
    """
    return '\033[{conf}m{content}\033[0m'.format(conf=conf, content=content)


# 执行cmd指令
def cmd(command, encoding='gb2312'):
    # 加了encoding后out为str，不加的话是 bytes，加encoding后流输出会换行
    result = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding=encoding)
    full_out = ''  # 执行结果
    while True:
        out = result.stdout.readline(1)  # limit -1：等待读完一行 1：读一个字符
        full_out += out
        sys.stdout.flush()  # 如果注释的话，会读完一行才显示
        if not out:
            break
    return full_out


# 列表分割
def list_chunk(lst, n):
    arr = []
    for i in range(0, len(lst), n):
        arr.append(lst[i:i + n])
    return arr


def array_column(array, column_key=None, index_key=None):
    """
    模拟PHP的array_column函数
    """
    if column_key is not None:
        return [row[column_key] for row in array]
    if index_key is not None:
        return {row[index_key]: row for row in array}
    return None


"""
sys._getframe().f_back.f_lineno                # 获取调用行号
sys._getframe().f_back.f_code.co_name          # 获取调用函数名
sys._getframe().f_back.f_code.co_filename      # 获取调用函数文件名
sys._getframe().f_lineno                       # 获取当前行号
sys._getframe().f_code.co_name                 # 获取当前函数名
sys._getframe().f_code.co_filename             # 获取当前函数所在文件名

sys.argv # 接收shell脚本传入的参数
sys.path.append(path) # 加入到python系统的环境变量
sys.argv[0] # 代码本身文件路径
sys.argv[1] # 第一个命令行参数
sys.path[0] # 此元素是在程序启动时初始化，自动寻找脚本的目录，所以亦是被运行脚本所在的真实目录

os.path.basename(__file__) # 当前文件名
os.path.dirname(__file__) # 当前目录名
os.path.split(__file__) # 分割成目录与文件
os.path.abspath(__file__) # 返回文件的真实路径，而非软链接所在的路径同os.path.realpath
os.getcwd() # 返回当前工作目录，同sys.path[0]
"""

from .LoggingFactory import LoggingFactory
from .ThreadExecutor import ThreadExecutor
