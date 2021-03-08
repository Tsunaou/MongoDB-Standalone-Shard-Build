import sys
import os
import argparse

IP = "114.212.84.175"
# 分片规划
SHARDS = ['shard1', 'shard2', 'config']
# 端口规划
PORTS = {
    'shard1': [27010, 27011, 27012],
    'shard2': [28010, 28011, 28012],
    'config': [29010, 29011, 29012]
}
# 工作目录
WORKSPACE = "/home/young/mongodb"

shardsvr_yaml_template = """sharding:
    clusterRole: shardsvr
replication:
    replSetName: {}
net:
    port: {}
    bindIp: 0.0.0.0
systemLog:
    destination: file
    logAppend: true
    path: {}/data/log/mongod{}/mongod.log
storage:
    dbPath: {}/data/db/db{}
    journal:
        enabled: true
processManagement:
    fork: true
    pidFilePath: {}/var/run/mongodb{}/mongod.pid
    timeZoneInfo: /usr/share/zoneinfo
security:
    keyFile: {}/data/keyfile/autokey{}/autokey
"""

configsvr_yaml_template = """sharding:
  clusterRole: configsvr  
replication:
  replSetName: {}  	 
net:
  port: {}              
  bindIp: 0.0.0.0        
systemLog:
  destination: file        
  logAppend: true		   
  path: {}/data/config/log/mongod{}/mongod.log    
storage:
  dbPath: {}/data/config/db/db{}              
  journal:
    enabled: true           
processManagement:
  fork: true               
  pidFilePath: {}/var/run/config/mongodb{}/mongod.pid
  timeZoneInfo: /usr/share/zoneinfo    
security:
  keyFile: {}/data/config/keyfile/autokey{}/autokey   
"""

def start_mongod(shard):
    for port in PORTS[shard]:
        if shard.__contains__("shard"):
            os.system("mongod -f {}/opt/mongos/conf{}/shard{}.yaml".format(WORKSPACE, port, port))
        elif shard.__contains__("config"):
            os.system("mongod -f {}/opt/configsvr/conf{}/config{}.yaml".format(WORKSPACE, port, port))

def restart_mongod(shard):
    yamls = {}
    for port in PORTS[shard]:
        if shard.__contains__("shard"):
            yamls["{}/opt/mongos/conf{}/shard{}.yaml".format(WORKSPACE, port, port)] \
                = shardsvr_yaml_template.format(shard, port, WORKSPACE, port, WORKSPACE, port, WORKSPACE, port,
                                                WORKSPACE, port)
        elif shard.__contains__("config"):
            yamls["{}/opt/configsvr/conf{}/config{}.yaml".format(WORKSPACE, port, port)] \
                = configsvr_yaml_template.format(shard, port, WORKSPACE, port, WORKSPACE, port, WORKSPACE, port,
                                                 WORKSPACE, port)
    for file, yaml in yamls.items():
        with open(file, 'w') as f:
            f.write(yaml)

    start_mongod(shard)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="start your mongodb service")
    parser.add_argument("-r", "--restart", help="Whether to change the security part in yaml",action="store_true")
    parser.add_argument("shard", help="Which shard to start")
    args = parser.parse_args()
    restart = args.restart
    shard = args.shard
    if restart:
        restart_mongod(shard)
    else:
        start_mongod(shard)