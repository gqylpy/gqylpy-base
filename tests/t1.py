import config

from tools import kube

pod_list = kube.oi_public_cluster.list_namespaced_pod('isddc')

for pod in pod_list.items:
    print(pod.status.phase, pod.metadata.name)
