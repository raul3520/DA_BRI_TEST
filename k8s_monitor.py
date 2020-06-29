from kubernetes import client,config
import mysql.connector
import sys
import os
from os import path
import json
def doc():
    '''Usage format is 
    for status python3 scriptname.py status.
    for k8s install update from you need a yaml file and syntax is
    python3 script.py podupdate <yaml file> install/upgrade'''
if len(sys.argv) <= 1 or sys.argv[1] == "-h":
    print(doc.__doc__)    
    sys.exit(1)
def status():
    config.load_kube_config()
    v1=client.CoreV1Api()

    ret=v1.list_namespaced_pod('default',watch="False")
    pods=ret.items
    podname= [pod.metadata.name for pod in pods]
    podstatus= [pod.status.phase for pod in pods ]
    podhost= [pod.status.host_ip for pod in pods]
    podhostname=[pod.spec.node_name for pod in pods]
    podmem=[]
    podcpu=[]
    nodemem=[]
    nodecpu=[]

    for pod in podname:
        cmd="sudo kubectl get --raw /apis/metrics.k8s.io/v1beta1/namespaces/default/pods/"+pod+"> temp.json"
        os.system(cmd)
        with open('temp.json') as f:
            data=json.load(f)
        memory=data.get('containers')[0].get('usage').get('cpu')
        cpu=data.get('containers')[0].get('usage').get('memory')
        podmem.append(memory)
        podcpu.append(cpu)
    print(podmem)
    print(podcpu)
    for node in podhostname:
        #print(node)
        cmd="kubectl get --raw /apis/metrics.k8s.io/v1beta1/nodes/"+node+"> temp.json"
        os.system(cmd)
        with open('temp.json') as f:
            data=json.load(f)
        cpu=data.get('usage').get('cpu')
        memory=data.get('usage').get('memory')
        nodemem.append(memory)
        nodecpu.append(cpu)
    print(nodemem)
    print(nodecpu)
    #print(pods)
    print(podhost)
    print(podhostname)
    print(podname)
    print(podstatus)
    print(list(zip(podname,podstatus,podhost,podhostname,podmem,podcpu,nodemem,nodecpu)))
    connection = mysql.connector.connect(host='10.142.0.3',
                                         user='root',
                                         password='root123',
                                         database='k8s')
    cursor = connection.cursor()
    for row in list(zip(podname,podstatus,podhost,podhostname,podmem,podcpu,nodemem,nodecpu)):
        cursor.execute("insert into stats(podname,state,nodeip,nodename,podcpu,podmem,nodemem,nodecpu) values(%s,%s,%s,%s,%s,%s,%s,%s)",(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))
    connection.commit()
    cursor.close()
    connection.close()

def podupdate(name):
    print("Hope you have used with syntax python3 scriptname podupdate yamlfile upgrade/install")
    print("The yaml file you mentioned is",name)
    if sys.argv[3] is "":
        sys.exit(1)
    if path.exists(name):
        if sys.argv[3] == "install":
            cmd="sudo kubectl create -f "+name
            os.system(cmd)
        elif sys.argv[3] == "upgrade":
            cmd="sudo kubectl apply -f "+name
            os.system(cmd)
        else:
            print("Please check the last parameter passed")
    else:
        print("yaml file not found")

if sys.argv[1] == "podupdate":
    podupdate(sys.argv[2])
if sys.argv[1] == "status":
    status()
