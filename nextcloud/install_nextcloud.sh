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

# 获取域名
get_domain() {
    read -p "请输入您的域名 (例如: cloud.example.com): " domain
    if [[ -z "$domain" ]]; then
        echo -e "${RED}域名不能为空${NC}"
        exit 1
    fi
    echo "$domain"
}

# 检测系统类型
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VERSION=$VERSION_ID
else
    echo -e "${RED}无法检测操作系统类型${NC}"
    exit 1
fi

# 检查Docker是否已安装
check_docker() {
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}Docker 已安装${NC}"
        return 0
    else
        echo -e "${YELLOW}Docker 未安装${NC}"
        return 1
    fi
}

# 检查Docker Compose是否已安装
check_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        echo -e "${GREEN}Docker Compose 已安装${NC}"
        return 0
    else
        echo -e "${YELLOW}Docker Compose 未安装${NC}"
        return 1
    fi
}

# 安装依赖
install_dependencies() {
    echo -e "${YELLOW}正在安装依赖...${NC}"
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        apt-get update
        apt-get install -y curl wget git apt-transport-https ca-certificates gnupg lsb-release certbot
    elif [[ "$OS" == *"CentOS"* ]]; then
        yum install -y curl wget git yum-utils device-mapper-persistent-data lvm2 certbot
    else
        echo -e "${RED}不支持的操作系统${NC}"
        exit 1
    fi
}

# 安装Docker
install_docker() {
    if check_docker; then
        return 0
    fi
    
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
    if check_docker_compose; then
        return 0
    fi
    
    echo -e "${YELLOW}正在安装Docker Compose...${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
}

# 创建Nextcloud配置目录
create_nextcloud_dirs() {
    echo -e "${YELLOW}创建Nextcloud配置目录...${NC}"
    mkdir -p nextcloud/{data,config,apps,theme,ssl,nginx}
    chmod -R 777 nextcloud
}

# 创建Nginx配置
create_nginx_config() {
    local domain=$1
    echo -e "${YELLOW}创建Nginx配置...${NC}"
    cat > nextcloud/nginx/nginx.conf << EOF
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    log_format main '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                    '\$status \$body_bytes_sent "\$http_referer" '
                    '"\$http_user_agent" "\$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log main;
    sendfile on;
    keepalive_timeout 65;
    client_max_body_size 10G;
    fastcgi_buffers 64 4K;
    gzip on;
    gzip_vary on;
    gzip_comp_level 4;
    gzip_min_length 256;
    gzip_proxied expired no-cache no-store private no_last_modified no_etag auth;
    gzip_types application/atom+xml application/javascript application/json application/ld+json application/manifest+json application/rss+xml application/vnd.geo+json application/vnd.ms-fontobject application/x-font-ttf application/x-web-app-manifest+json application/xhtml+xml application/xml font/opentype image/bmp image/svg+xml image/x-icon text/cache-manifest text/css text/plain text/vcard text/vnd.rim.location.xloc text/vtt text/x-component text/x-cross-domain-policy;

    server {
        listen 80;
        server_name $domain;
        return 301 https://\$server_name\$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name $domain;

        ssl_certificate /etc/ssl/private/fullchain.pem;
        ssl_certificate_key /etc/ssl/private/privkey.pem;
        ssl_session_timeout 1d;
        ssl_session_cache shared:SSL:50m;
        ssl_session_tickets off;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_stapling on;
        ssl_stapling_verify on;
        add_header Strict-Transport-Security "max-age=31536000" always;

        location / {
            proxy_pass http://nextcloud:80;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_set_header X-Forwarded-Host \$host;
            proxy_set_header X-Forwarded-Port \$server_port;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }
    }
}
EOF
}

# 申请SSL证书
request_ssl_certificate() {
    local domain=$1
    echo -e "${YELLOW}正在申请SSL证书...${NC}"
    
    # 停止nginx容器（如果存在）
    docker-compose down
    
    # 申请证书
    certbot certonly --standalone -d "$domain" --agree-tos --email admin@$domain --non-interactive
    
    # 复制证书到Nextcloud目录
    cp /etc/letsencrypt/live/$domain/fullchain.pem nextcloud/ssl/
    cp /etc/letsencrypt/live/$domain/privkey.pem nextcloud/ssl/
    
    # 设置证书权限
    chmod -R 755 nextcloud/ssl
}

# 创建docker-compose.yml
create_docker_compose() {
    local domain=$1
    echo -e "${YELLOW}创建docker-compose.yml...${NC}"
    cat > docker-compose.yml << EOF
version: '3'

services:
  nginx:
    image: nginx:alpine
    container_name: nextcloud_nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nextcloud/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nextcloud/ssl:/etc/ssl/private:ro
    depends_on:
      - nextcloud
    networks:
      - nextcloud_network
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 10s
      timeout: 5s
      retries: 3

  nextcloud:
    image: nextcloud:latest
    container_name: nextcloud
    restart: always
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
      - NEXTCLOUD_TRUSTED_DOMAINS=$domain
      - PHP_MEMORY_LIMIT=512M
      - PHP_UPLOAD_LIMIT=10G
      - PHP_MAX_EXECUTION_TIME=3600
      - PHP_MAX_INPUT_TIME=3600
      - PHP_OPCACHE_ENABLE=1
      - PHP_OPCACHE_MEMORY_CONSUMPTION=128
      - PHP_OPCACHE_INTERNED_STRINGS_BUFFER=8
      - PHP_OPCACHE_MAX_ACCELERATED_FILES=4000
      - PHP_OPCACHE_REVALIDATE_FREQ=60
      - PHP_OPCACHE_FAST_SHUTDOWN=1
      - PHP_OPCACHE_ENABLE_CLI=1
      - PHP_APCU_ENABLE=1
      - PHP_APCU_MEMORY_CONSUMPTION=128
      - PHP_APCU_TTL=7200
      - PHP_APCU_GC_TTL=3600
      - PHP_APCU_ENABLE_CLI=1
      - PHP_REDIS_ENABLE=1
      - PHP_REDIS_HOST=redis
      - PHP_REDIS_PORT=6379
    depends_on:
      - db
      - redis
    networks:
      - nextcloud_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/index.php/status"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

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
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p$$MYSQL_ROOT_PASSWORD"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  redis:
    image: redis:alpine
    container_name: nextcloud_redis
    restart: always
    networks:
      - nextcloud_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

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

# 等待服务健康
wait_for_services() {
    echo -e "${YELLOW}等待服务启动...${NC}"
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps | grep -q "healthy"; then
            echo -e "${GREEN}所有服务已健康启动${NC}"
            return 0
        fi
        echo -e "${YELLOW}等待服务健康检查... (尝试 $attempt/$max_attempts)${NC}"
        sleep 10
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}服务健康检查超时${NC}"
    return 1
}

# 主函数
main() {
    echo -e "${GREEN}开始安装Nextcloud...${NC}"
    
    # 获取域名
    domain=$(get_domain)
    
    install_dependencies
    install_docker
    install_docker_compose
    create_nextcloud_dirs
    create_nginx_config "$domain"
    request_ssl_certificate "$domain"
    create_docker_compose "$domain"
    optimize_system
    
    echo -e "${GREEN}启动Nextcloud...${NC}"
    docker-compose down -v  # 清理旧容器
    docker-compose up -d
    
    # 等待服务健康
    if ! wait_for_services; then
        echo -e "${RED}服务启动失败，请检查日志${NC}"
        docker-compose logs
        exit 1
    fi
    
    echo -e "${GREEN}安装完成！${NC}"
    echo -e "Nextcloud 访问地址: https://$domain"
    echo -e "默认管理员账号: admin"
    echo -e "默认管理员密码: admin"
    echo -e "${YELLOW}请及时修改默认密码！${NC}"
}

# 执行主函数
main 