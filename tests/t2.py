import config as _
from tools import retry


@retry(count=3, cycle=1)
def func():
    int('a')


func()
