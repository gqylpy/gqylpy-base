import time
import config
from tools import decorator


@decorator.record_time
def get_data():
    time.sleep(1.4)


get_data()
