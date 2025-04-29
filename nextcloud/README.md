# Nextcloud 自动安装脚本

这是一个自动安装和优化 Nextcloud 的脚本，支持 Ubuntu、Debian 和 CentOS 系统。

## 功能特点

- 自动检测系统类型并安装相应依赖
- 自动安装 Docker 和 Docker Compose
- 配置优化的 Nextcloud 环境
- 系统性能优化
- 支持 MariaDB 数据库
- 支持 Redis 缓存
- 自动配置网络和存储

## 系统要求

- Ubuntu 18.04+ / Debian 10+ / CentOS 7+
- 至少 2GB RAM
- 至少 20GB 可用磁盘空间
- 需要 root 权限

## 安装步骤

1. 下载脚本：
```bash
wget https://raw.githubusercontent.com/your-repo/nextcloud/main/install_nextcloud.sh
```

2. 添加执行权限：
```bash
chmod +x install_nextcloud.sh
```

3. 运行安装脚本：
```bash
sudo ./install_nextcloud.sh
```

## 性能优化

脚本包含以下优化：

1. 系统优化：
   - 增加文件描述符限制
   - 优化内核网络参数
   - 优化 TCP 连接参数

2. 数据库优化：
   - 配置 InnoDB 缓冲池
   - 优化日志文件大小
   - 优化事务提交方式

3. Nextcloud 优化：
   - 增加 PHP 内存限制
   - 增加上传文件大小限制
   - 增加执行时间限制
   - 启用 Redis 缓存

## 默认配置

- 访问地址：http://localhost
- 默认管理员账号：admin
- 默认管理员密码：admin
- 数据库用户：nextcloud
- 数据库密码：nextcloud_password
- 数据库 root 密码：root_password

## 安全建议

1. 安装完成后立即修改默认密码
2. 配置 SSL 证书
3. 设置防火墙规则
4. 定期备份数据

## 故障排除

如果遇到问题，请检查：

1. Docker 服务是否正常运行
2. 端口 80 是否被占用
3. 系统日志中是否有错误信息
4. 磁盘空间是否充足

## 维护命令

- 查看容器状态：`docker-compose ps`
- 查看日志：`docker-compose logs -f`
- 重启服务：`docker-compose restart`
- 停止服务：`docker-compose down`
- 更新镜像：`docker-compose pull`

## 许可证

MIT License 