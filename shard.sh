#!/bin/bash
# 2 部署分配
# 2.2.1 Pid文件路径
mkdir -p /home/young/mongodb/var/run/mongodb27010
mkdir -p /home/young/mongodb/var/run/mongodb27011
mkdir -p /home/young/mongodb/var/run/mongodb27012
touch /home/young/mongodb/var/run/mongodb2701{0,1,2}/mongod.pid
# 2.2.2 日志存储路径
mkdir -p /home/young/mongodb/data/log/mongod27010
mkdir -p /home/young/mongodb/data/log/mongod27011
mkdir -p /home/young/mongodb/data/log/mongod27012
touch /home/young/mongodb/data/log/mongod2701{0,1,2}/mongod.log
# 2.2.3 分片数据存储路径
mkdir -p /home/young/mongodb/data/db/db27010
mkdir -p /home/young/mongodb/data/db/db27011
mkdir -p /home/young/mongodb/data/db/db27012
# 2.2.4 keyfile文件路径
mkdir -p /home/young/mongodb/data/keyfile/autokey27010
mkdir -p /home/young/mongodb/data/keyfile/autokey27011
mkdir -p /home/young/mongodb/data/keyfile/autokey27012
touch /home/young/mongodb/data/keyfile/autokey2701{0,1,2}/autokey
# 生成keyfile文件（所有的keyfile保持一致）：
openssl rand -base64 756 > /home/young/mongodb/data/keyfile/autokey27010/autokey
 
cp /home/young/mongodb/data/keyfile/autokey27010/autokey /home/young/mongodb/data/keyfile/autokey27011/
cp /home/young/mongodb/data/keyfile/autokey27010/autokey /home/young/mongodb/data/keyfile/autokey27012/

chmod 400 /home/young/mongodb/data/keyfile/autokey27010/autokey
chmod 400 /home/young/mongodb/data/keyfile/autokey27011/autokey
chmod 400 /home/young/mongodb/data/keyfile/autokey27012/autokey

# 2.4 分片副本集配置数据
mkdir -p /home/young/mongodb/opt/mongos/conf2701{0,1,2}

