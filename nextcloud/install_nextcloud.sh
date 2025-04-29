#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}请使用root权限运行此脚本${NC}"
    exit 1
fi

# 检测系统类型
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VERSION=$VERSION_ID
else
    echo -e "${RED}无法检测操作系统类型${NC}"
    exit 1
fi

# 安装依赖
install_dependencies() {
    echo -e "${YELLOW}正在安装依赖...${NC}"
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        apt-get update
        apt-get install -y curl wget git apt-transport-https ca-certificates gnupg lsb-release
    elif [[ "$OS" == *"CentOS"* ]]; then
        yum install -y curl wget git yum-utils device-mapper-persistent-data lvm2
    else
        echo -e "${RED}不支持的操作系统${NC}"
        exit 1
    fi
}

# 安装Docker
install_docker() {
    echo -e "${YELLOW}正在安装Docker...${NC}"
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        curl -fsSL https://get.docker.com | sh
    elif [[ "$OS" == *"CentOS"* ]]; then
        yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        yum install -y docker-ce docker-ce-cli containerd.io
    fi
    
    systemctl enable docker
    systemctl start docker
}

# 安装Docker Compose
install_docker_compose() {
    echo -e "${YELLOW}正在安装Docker Compose...${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
}

# 创建Nextcloud配置目录
create_nextcloud_dirs() {
    echo -e "${YELLOW}创建Nextcloud配置目录...${NC}"
    mkdir -p nextcloud/{data,config,apps,theme}
    chmod -R 777 nextcloud
}

# 创建docker-compose.yml
create_docker_compose() {
    echo -e "${YELLOW}创建docker-compose.yml...${NC}"
    cat > docker-compose.yml << 'EOF'
version: '3'

services:
  nextcloud:
    image: nextcloud:latest
    container_name: nextcloud
    restart: always
    ports:
      - "80:80"
    volumes:
      - ./nextcloud/data:/var/www/html/data
      - ./nextcloud/config:/var/www/html/config
      - ./nextcloud/apps:/var/www/html/custom_apps
      - ./nextcloud/theme:/var/www/html/themes
    environment:
      - MYSQL_HOST=db
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_PASSWORD=nextcloud_password
      - NEXTCLOUD_TRUSTED_DOMAINS=localhost
      - PHP_MEMORY_LIMIT=512M
      - PHP_UPLOAD_LIMIT=10G
      - PHP_MAX_EXECUTION_TIME=3600
      - PHP_MAX_INPUT_TIME=3600
    depends_on:
      - db
    networks:
      - nextcloud_network

  db:
    image: mariadb:10.6
    container_name: nextcloud_db
    restart: always
    volumes:
      - ./nextcloud/db:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=root_password
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_PASSWORD=nextcloud_password
    command: --innodb-buffer-pool-size=1G --innodb-log-file-size=256M --innodb-flush-method=O_DSYNC --innodb-flush-log-at-trx-commit=2
    networks:
      - nextcloud_network

  redis:
    image: redis:alpine
    container_name: nextcloud_redis
    restart: always
    networks:
      - nextcloud_network

networks:
  nextcloud_network:
    driver: bridge
EOF
}

# 优化系统设置
optimize_system() {
    echo -e "${YELLOW}优化系统设置...${NC}"
    # 增加文件描述符限制
    cat > /etc/security/limits.d/nextcloud.conf << 'EOF'
* soft nofile 65535
* hard nofile 65535
EOF

    # 优化内核参数
    cat > /etc/sysctl.d/99-nextcloud.conf << 'EOF'
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 1200
net.ipv4.tcp_max_tw_buckets = 65535
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_timestamps = 1
net.ipv4.tcp_slow_start_after_idle = 0
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 87380 16777216
EOF

    # 应用内核参数
    sysctl -p /etc/sysctl.d/99-nextcloud.conf
}

# 主函数
main() {
    echo -e "${GREEN}开始安装Nextcloud...${NC}"
    
    install_dependencies
    install_docker
    install_docker_compose
    create_nextcloud_dirs
    create_docker_compose
    optimize_system
    
    echo -e "${GREEN}启动Nextcloud...${NC}"
    docker-compose up -d
    
    echo -e "${GREEN}安装完成！${NC}"
    echo -e "Nextcloud 访问地址: http://localhost"
    echo -e "默认管理员账号: admin"
    echo -e "默认管理员密码: admin"
    echo -e "${YELLOW}请及时修改默认密码！${NC}"
}

# 执行主函数
main 