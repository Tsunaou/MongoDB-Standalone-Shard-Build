import sys
import os

IP = "114.212.84.175"
# 分片规划
SHARDS = ['shard1', 'shard2', 'config']
# 端口规划
PORTS = {
    'shard1' : [27010, 27011, 27012],
    'shard2' : [28010, 28011, 28012],
    'config' : [29010, 29011, 29012]
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
#security:
    #keyFile: {}/data/keyfile/autokey{}/autokey
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
#security:
  #keyFile: {}/data/config/keyfile/autokey{}/autokey   
"""

mongos_yaml_template = """sharding:
    configDB: config/{}
net:
    port: 27017
    bindIp: 0.0.0.0
 
systemLog:
    destination: file
    logAppend: true
    path: {}/data/mongos/log/route.log
 
processManagement:
    fork: true
    pidFilePath: {}/data/mongos/pidfile/mongos.pid
    timeZoneInfo: /usr/share/zoneinfo
 
# security:
#   keyFile: {}/data/mongos/keyfile/autokey
"""

if __name__ == '__main__':

    # 待执行命令
    commands = []
    yamls = {}

    # shard和config server设置
    for shard in SHARDS:
        if PORTS[shard].__len__() == 0:
            continue

        for port in PORTS[shard]:
            if shard.__contains__("shard"):
                # Pid文件路径
                commands.append("mkdir -p {}/var/run/mongodb{}".format(WORKSPACE, port))
                commands.append("touch {}/var/run/mongodb{}/mongod.pid".format(WORKSPACE, port))
                # 日志存储路径
                commands.append("mkdir -p {}/data/log/mongod{}".format(WORKSPACE, port))
                commands.append("touch {}/data/log/mongod{}/mongod.log".format(WORKSPACE, port))
                # 分片数据存储路径
                commands.append("mkdir -p {}/data/db/db{}".format(WORKSPACE, port))
                # keyfile文件路径
                commands.append("mkdir -p {}/data/keyfile/autokey{}".format(WORKSPACE, port))
                commands.append("touch {}/data/keyfile/autokey{}/autokey".format(WORKSPACE, port))
            elif shard.__contains__("config"):
                # Pid文件路径
                commands.append("mkdir -p {}/var/run/config/mongodb{}".format(WORKSPACE, port))
                commands.append("touch {}/var/run/config/mongodb{}/mongod.pid".format(WORKSPACE, port))
                # 日志存储路径
                commands.append("mkdir -p {}/data/config/log/mongod{}".format(WORKSPACE, port))
                commands.append("touch {}/data/config/log/mongod{}/mongod.log".format(WORKSPACE, port))
                # 分片数据存储路径
                commands.append("mkdir -p {}/data/config/db/db{}".format(WORKSPACE, port))
                # keyfile文件路径
                commands.append("mkdir -p {}/data/config/keyfile/autokey{}".format(WORKSPACE, port))
                commands.append("touch {}/data/config/keyfile/autokey{}/autokey".format(WORKSPACE, port))

        # 生成keyfile文件（所有的keyfile保持一致）
        if shard.__contains__("shard"):
            port0 = PORTS[shard][0]
            commands.append("openssl rand -base64 756 > {}/data/keyfile/autokey{}/autokey".format(WORKSPACE, port0))
            for port in PORTS[shard]:
                # 跳过第一个
                if port != port0:
                    commands.append("cp {}/data/keyfile/autokey{}/autokey {}/data/keyfile/autokey{}/".format(WORKSPACE, port0, WORKSPACE, port))
                commands.append("chmod 400 {}/data/keyfile/autokey{}/autokey".format(WORKSPACE, port))
        elif shard.__contains__("config"):
            port0 = PORTS[shard][0]
            commands.append("openssl rand -base64 756 > {}/data/config/keyfile/autokey{}/autokey".format(WORKSPACE, port0))
            for port in PORTS[shard]:
                # 跳过第一个
                if port != port0:
                    commands.append("cp {}/data/config/keyfile/autokey{}/autokey {}/data/config/keyfile/autokey{}/".format(WORKSPACE, port0, WORKSPACE, port))
                commands.append("chmod 400 {}/data/config/keyfile/autokey{}/autokey".format(WORKSPACE, port))
        # 分片副本集配置数据
        # 配置文件路径

        for port in PORTS[shard]:
            if shard.__contains__("shard"):
                commands.append("mkdir -p {}/opt/mongos/conf{}".format(WORKSPACE, port))
                yamls["{}/opt/mongos/conf{}/shard{}.yaml".format(WORKSPACE, port, port)] \
                    = shardsvr_yaml_template.format(shard, port, WORKSPACE, port, WORKSPACE, port, WORKSPACE, port, WORKSPACE, port)
            elif shard.__contains__("config"):
                commands.append("mkdir -p {}/opt/configsvr/conf{}".format(WORKSPACE, port))
                yamls["{}/opt/configsvr/conf{}/config{}.yaml".format(WORKSPACE, port, port)] \
                    = configsvr_yaml_template.format(shard, port, WORKSPACE, port, WORKSPACE, port, WORKSPACE, port, WORKSPACE, port)

    # mongos路由设置
    # 日志存储路径
    commands.append("mkdir -p {}/data/mongos/log/".format(WORKSPACE))
    commands.append("touch {}/data/mongos/log/route.log".format(WORKSPACE))
    # keyfile
    commands.append("mkdir -p {}/data/mongos/keyfile/".format(WORKSPACE))
    commands.append("touch {}/data/mongos/keyfile/autokey".format(WORKSPACE))
    commands.append("openssl rand -base64 756 > {}/data/mongos/keyfile/autokey".format(WORKSPACE))
    commands.append("chmod 400 {}/data/mongos/keyfile/autokey".format(WORKSPACE))
    # pid 文件路径
    commands.append("mkdir -p {}/data/mongos/pidfile".format(WORKSPACE))
    commands.append("touch {}/data/mongos/pidfile/mongos.pid".format(WORKSPACE))
    # mongos yaml 配置文件
    configDB  = ""
    if "config" in PORTS.keys():
        for port in PORTS["config"]:
            configDB = configDB + "{}:{},".format(IP, port)
        if configDB != "" and configDB[-1] == ',':
            configDB = configDB.strip(',')

    if configDB == "":
        sys.exit(-1)

    yamls["{}/opt/mongoroute/mongoroute.yaml".format(WORKSPACE)] = mongos_yaml_template.format(configDB, WORKSPACE, WORKSPACE, WORKSPACE)
    commands.append("mkdir -p {}/opt/mongoroute".format(WORKSPACE))
    for cmd in commands:
        os.system(cmd)

    for file, yaml in yamls.items():
        with open(file, 'w') as f:
            f.write(yaml)
