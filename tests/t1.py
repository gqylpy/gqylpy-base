import random
import config as __
from tools import aliyun

code = '{\"code\": %s}' % ''.join([str(random.randint(0, 9)) for i in range(4)])

aliyun.send_sms(TemplateParam={
    'name': 'EdgeAgent',
    'exc_location': 'Collector',
    'exc_type': 'AssertionError',
    'exc_info': 'in MEC.GatewayCollector, response code: 500, error message recorded in log/83d502.json'
})
