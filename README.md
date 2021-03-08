# MongoDB 4.2 单机分片测试集群搭建

- 本集群用于测试，这里关于kill后重启增加安全验证的可以忽略。
- 涉及到root和安全验证容易出一些额外的bug，个人建议测试时直接略过，在内网数据安全也得以保证

## 1 安装背景

### 1.1 实验环境

#### 1.1.1 分片集群架构图

#### 1.1.2 实验主机

| 主机             | IP             |
| ---------------- | -------------- |
| Ubuntu 20.04 LTS | 114.212.84.175 |

#### 1.1.3 端口规划

| 服务器           | 端口  |
| ---------------- | ----- |
| route1           | 27017 |
| conf1            | 29010 |
| conf2            | 29011 |
| conf3            | 29012 |
| shard1_primary   | 27010 |
| shard1_secondary | 27011 |
| shard1_arbiter   | 27012 |
| shard2_primary   | 28010 |
| shard2_secondary | 28011 |
| shard2_arbiter   | 28012 |

### 1.2 安装包下载

这里的目的是自己编译mongodb，编译生成的可执行文件在以下目录

```bash
/home/young/Programs/mongo/build/opt/mongo
```

因此可以创建软连接在`/bin`目录下便于后续访问，也省的每次重新编译后更改

```bash
sudo ln -sv /home/young/Programs/mongo/build/opt/mongo/mongod /bin/mongod
sudo ln -sv /home/young/Programs/mongo/build/opt/mongo/mongos /bin/mongos
sudo ln -sv /home/young/Programs/mongo/build/opt/mongo/mongo  /bin/mongo
```



## 2 部署分片

### 2.1 端口规划 

```bash
# 分片1
shard1:rs-1:27010
shard1:rs-1:27011
shard1:rs-1:27012
# 分片2
shard2:rs-2:28010
shard2:rs-2:28011
shard2:rs-2:28012
```

### 2.2 数据目录和文件创建生成

这里我用了一个python脚本来执行，详见[build_mongo.py](https://github.com/Tsunaou/MongoDB-Standalone-Shard-Build/blob/main/build_mongo.py)。
修改`build_mongo.py`中的工作目录地址`WORKSPACE`，有生成目录如下

```bash
$ python3 ./build_mongo.py
├── add_root.js
├── build_mongo.py
├── data
│   ├── config
│   │   ├── db
│   │   │   ├── db29010
│   │   │   ├── db29011
│   │   │   └── db29012
│   │   ├── keyfile
│   │   │   ├── autokey29010
│   │   │   │   └── autokey
│   │   │   ├── autokey29011
│   │   │   │   └── autokey
│   │   │   └── autokey29012
│   │   │       └── autokey
│   │   └── log
│   │       ├── mongod29010
│   │       │   └── mongod.log
│   │       ├── mongod29011
│   │       │   └── mongod.log
│   │       └── mongod29012
│   │           └── mongod.log
│   ├── db
│   │   ├── db27010
│   │   ├── db27011
│   │   ├── db27012
│   │   ├── db28010
│   │   ├── db28011
│   │   └── db28012
│   ├── keyfile
│   │   ├── autokey27010
│   │   │   └── autokey
│   │   ├── autokey27011
│   │   │   └── autokey
│   │   ├── autokey27012
│   │   │   └── autokey
│   │   ├── autokey28010
│   │   │   └── autokey
│   │   ├── autokey28011
│   │   │   └── autokey
│   │   └── autokey28012
│   │       └── autokey
│   ├── log
│   │   ├── mongod27010
│   │   │   └── mongod.log
│   │   ├── mongod27011
│   │   │   └── mongod.log
│   │   ├── mongod27012
│   │   │   └── mongod.log
│   │   ├── mongod28010
│   │   │   └── mongod.log
│   │   ├── mongod28011
│   │   │   └── mongod.log
│   │   └── mongod28012
│   │       └── mongod.log
│   └── mongos
│       ├── keyfile
│       │   └── autokey
│       ├── log
│       │   └── route.log
│       └── pidfile
│           └── mongos.pid
├── delete_dir.sh
├── init_config.js
├── init_shard1.js
├── init_shard2.js
├── opt
│   ├── configsvr
│   │   ├── conf29010
│   │   │   └── config29010.yaml
│   │   ├── conf29011
│   │   │   └── config29011.yaml
│   │   └── conf29012
│   │       └── config29012.yaml
│   ├── mongoroute
│   │   └── mongoroute.yaml
│   └── mongos
│       ├── conf27010
│       │   └── shard27010.yaml
│       ├── conf27011
│       │   └── shard27011.yaml
│       ├── conf27012
│       │   └── shard27012.yaml
│       ├── conf28010
│       │   └── shard28010.yaml
│       ├── conf28011
│       │   └── shard28011.yaml
│       └── conf28012
│           └── shard28012.yaml
├── shard.sh
├── start_service.py
└── var
    └── run
        ├── config
        │   ├── mongodb29010
        │   │   └── mongod.pid
        │   ├── mongodb29011
        │   │   └── mongod.pid
        │   └── mongodb29012
        │       └── mongod.pid
        ├── mongodb27010
        │   └── mongod.pid
        ├── mongodb27011
        │   └── mongod.pid
        ├── mongodb27012
        │   └── mongod.pid
        ├── mongodb28010
        │   └── mongod.pid
        ├── mongodb28011
        │   └── mongod.pid
        └── mongodb28012
            └── mongod.pid
```

## 3 配置并启动服务器与分片集群

### 3.1 启动分片副本集与配置服务器还有mongos路由

#### 3.1.1 启动配置服务器（config），并进行初始化

首先将yaml配置文件中的security部分注释掉，然后启动（这里介绍一下命令，后续用脚本[start_service.py](https://github.com/Tsunaou/MongoDB-Standalone-Shard-Build/blob/main/start_service.py)）：

```bash
mongod -f /home/young/mongodb/opt/configsvr/conf29010/config29010.yaml
mongod -f /home/young/mongodb/opt/configsvr/conf29011/config29011.yaml
mongod -f /home/young/mongodb/opt/configsvr/conf29012/config29012.yaml
```

然后登入primary节点，进行初始化，载入初始化脚本。

> 注意 _id:副本集名称要和config.yaml中的replSetName配置名称相同; 只需初始化一次即可

```bash
$ mongo --port 29010
> load("init_config.js")
```

初始化脚本`init_config.js`如下

```javascript
rs.initiate(
    {
        _id: "config",
        configsvr: true,
        members: [
            { _id : 0, host : "114.212.84.175:29010" },
            { _id : 1, host : "114.212.84.175:29011" },
            { _id : 2, host : "114.212.84.175:29012" }
        ]
    }
);
rs.status();
```

> ------
>
> **以下安全所需，测试时可以略过***

之后，为conf集群添加root用户

> 1. 这里必须要连接到primary节点下创建用户,在secondary节点上创建用户会报错
> 2. 连接上primary节点后,一定要切换到admin数据库下创建root用户

```bash
$ mongo --port 29010
config:PRIMARY> use admin
config:PRIMARY> load("add_root.js")
```

之后，kill掉mongod进程，解除config.yaml配置文件中的security认证注释，重启mongod

```bash
 kill `ps -ef|grep mongo|awk {'print $2'}`
```

然后重启conf服务

```bash
$ python3 ./start_service.py --restart config
```

之后登陆mongo shell

```bash
$ mongo --port 29010      #这里需要注意，重启后primary不一定是29010
config:PRIMARY> use admin               #切换到admin数据库
config:PRIMARY> db.auth('root','root')  #登录 返回1说明登录成功
 
# 登陆后：
config:PRIMARY> show dbs;
config:PRIMARY> rs.status()
```

成功输出如下。

```bash
config:PRIMARY> show dbs;
admin   0.000GB
config  0.000GB
local   0.000GB
```

#### 3.1.2 启动分片副本集1，并进行初始化

使用yaml文件启动

```bash
python3 ./start_service.py shard1
```

初始化(一主一从一仲裁）

```bash
$ mongo --port 27010
> load("init_shard1.js")
```

> ***以下安全所需，测试时可以略过***

为share1添加root用户(必须在PRIMARY状态下，可以按回车键可以看到PRIMARY）

```bash
$ mongo --port 27010
config:PRIMARY> use admin
config:PRIMARY> load("add_root.js")
```

kill掉mongod服务进程,把shard1.yaml配置文件中的security认证注释打开,重启mongod服务：

```bash
kill `ps -ef |grep 'mongod -f /home/young/mongodb/opt/mongos/conf270'|awk {'print $2'}`
```

重启mongod服务

```bash
python3 ./start_service.py --restart shard1
```

之后登陆mongo shell

```bash
$ mongo --port 27010      #这里需要注意，重启后primary不一定是29010
config:PRIMARY> use admin               #切换到admin数据库
config:PRIMARY> db.auth('root','root')  #登录 返回1说明登录成功
 
# 登陆后：
config:PRIMARY> show dbs;
config:PRIMARY> rs.status()
```

成功输出如下。

```bash
config:PRIMARY> show dbs;
admin   0.000GB
config  0.000GB
local   0.000GB
```

#### 3.1.3 启动分片副本集2，并进行初始化

使用yaml文件启动

```bash
python3 ./start_service.py shard2
```

初始化(一主一从一仲裁）

```bash
$ mongo --port 28010
> load("init_shard2.js")
```

> ***以下安全所需，测试时可以略过***

为share1添加root用户(必须在PRIMARY状态下，可以按回车键可以看到PRIMARY）

```bash
$ mongo --port 28010
config:PRIMARY> use admin
config:PRIMARY> load("add_root.js")
```

kill掉mongod服务进程,把shard1.yaml配置文件中的security认证注释打开,重启mongod服务：

```bash
kill `ps -ef |grep 'mongod -f /home/young/mongodb/opt/mongos/conf280'|awk {'print $2'}`
```

重启mongod服务

```bash
python3 ./start_service.py --restart shard2
```

之后登陆mongo shell

```bash
$ mongo --port 28010      #这里需要注意，重启后primary不一定是29010
config:PRIMARY> use admin               #切换到admin数据库
config:PRIMARY> db.auth('root','root')  #登录 返回1说明登录成功
 
# 登陆后：
config:PRIMARY> show dbs;
config:PRIMARY> rs.status()
```

成功输出如下。

```bash
config:PRIMARY> show dbs;
admin   0.000GB
config  0.000GB
local   0.000GB
```

#### 3.1.4 启动route路由集群，并整合conf集群和shard集群

启动route

```bash
mongos -f /home/young/mongodb/opt/mongoroute/mongoroute.yaml
```

添加shard分片集群

```javascript
$ mongo
use admin;
sh.addShard( "shard1/114.212.84.175:27010");
sh.addShard( "shard2/114.212.84.175:28010");
sh.status() 
```

开启均衡器

```bash
mongos> sh.startBalancer()
```



## 参考

- [mongodb4.2.8单机分片集群搭建](https://blog.csdn.net/weixin_44800915/article/details/106924558)