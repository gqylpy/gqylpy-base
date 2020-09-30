import sys
import tools as gqy

from .decorator import retry
from kubernetes import client as kube_client

__ = sys.modules[__name__]


@retry('InitKube', cycle=60)
def __init__(config: gqy.gdict):
    kube: gqy.gdict = config.kube
    init: gqy.gdict = kube.pop('init', {})

    for name, conf in kube.items():

        for item in init.items():
            conf.setdefault(*item)

        kube_config = kube_client.Configuration()
        kube_config.host = f'{conf.protocol}://{conf.api_server}'
        kube_config.verify_ssl = conf.verify_ssl
        kube_config.api_key = {'authorization': 'Bearer ' + conf.token.strip()}

        api_client = kube_client.ApiClient(kube_config)
        kube_api = getattr(kube_client, conf.load_apis[0])(api_client)

        for api_str in conf.load_apis[1:]:
            api_obj = getattr(kube_client, api_str)(api_client)

            for method_str in dir(api_obj):
                method_obj = getattr(api_obj, method_str)

                if not method_str.startswith('_') and callable(method_obj):
                    setattr(kube_api, method_str, method_obj)

        setattr(__, name, kube_api)


mec_cluster: kube_client.CoreV1Api
oi219_cluster: kube_client.CoreV1Api
oi_public_cluster: kube_client.CoreV1Api

"""
apiVersion: v1
kind: ServiceAccount
metadata:
  name: gqylpy-base
  namespace: kube-system

---

apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRoleBinding
metadata:
  name: gqylpy-base
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
  - kind: ServiceAccount
    name: gqylpy-base
    namespace: kube-system
"""
