# TencentCloud_Tool

CDB汇总脚本


备注：
	MySQL目录下脚本自动获取CDB信息（项目名，实例名，ip地址，备份状态，磁盘使用率等）汇总并发送邮件，方便查看与管理
	Redis目录下脚本自动获取redis信息（项目名，实例名，ip地址，内存使用率等）汇总并发送邮件，方便查看与管理
	Disaster Recover 目录下脚本进行容灾演练切换
	



数据库中创建如下表：

1.备份信息表
```
CREATE TABLE `backup_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_name` varchar(128) DEFAULT NULL COMMENT '项目名称',
  `backup_name` varchar(128) DEFAULT NULL COMMENT '备份集名称',
  `start_time` datetime DEFAULT NULL COMMENT '备份开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '备份结束时间',
  `backup_status` varchar(10) DEFAULT NULL COMMENT '备份状态',
  `backup_type` varchar(10) DEFAULT NULL COMMENT '备份类型（logical or physics）',
  `backup_size` float(10,2) DEFAULT NULL COMMENT '备份大小（M）',
  `internetUrl` varchar(1024) DEFAULT NULL COMMENT '外网下载地址',
  `intranetUrl` varchar(1024) DEFAULT NULL COMMENT '内网下载地址',
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10163 DEFAULT CHARSET=utf8;
```

2.DB信息表
```
CREATE TABLE `db_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_name` varchar(30) DEFAULT NULL COMMENT '项目名称',
  `masterSID` varchar(20) DEFAULT NULL COMMENT '主实例SID',
  `masterIP` varchar(20) DEFAULT NULL COMMENT '主实例IP',
  `slaveSID` varchar(20) DEFAULT '0' COMMENT '从库实例SID',
  `slaveIP` varchar(20) DEFAULT '0' COMMENT '从实例ip',
  `drSID` varchar(20) DEFAULT '0' COMMENT '灾备SID',
  `drIP` varchar(20) DEFAULT '0' COMMENT '灾备实例IP',
  `disk_total` int(10) DEFAULT NULL COMMENT '磁盘总大小，单位G',
  `disk_usage` int(10) DEFAULT NULL COMMENT '磁盘使用大小，单位G',
  `disk_percent` float(10,2) DEFAULT NULL COMMENT '磁盘使用占比',
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ind_created` (`created`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=11289 DEFAULT CHARSET=utf8;
```

3.MySQL分区表信息
```
CREATE TABLE `partition_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_name` varchar(30) DEFAULT NULL COMMENT '项目名称',
  `ip` varchar(20) DEFAULT NULL COMMENT 'ip地址',
  `dbname` varchar(128) DEFAULT NULL COMMENT 'db名',
  `table_name` varchar(128) DEFAULT NULL COMMENT '表名',
  `max_partition` varchar(10) DEFAULT NULL COMMENT '最大的分区',
  `max_partition_time` varchar(20) DEFAULT NULL COMMENT '最大分区时间',
  `expired_time` varchar(20) DEFAULT NULL COMMENT '过期时间',
  `created` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5951 DEFAULT CHARSET=utf8;
```

4.redis实例信息
```
CREATE TABLE `redis_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_name` varchar(64) DEFAULT NULL,
  `sid` varchar(32) DEFAULT NULL,
  `ip` varchar(32) DEFAULT NULL,
  `port` int(10) DEFAULT NULL,
  `usage_size` float(10,2) DEFAULT NULL,
  `total_size` int(10) DEFAULT NULL,
  `created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10613 DEFAULT CHARSET=utf8;
```






