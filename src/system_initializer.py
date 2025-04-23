import subprocess
from typing import Dict, Optional
from .system_detector import SystemDetector

class SystemInitializer:
    def __init__(self):
        self.dist_info = SystemDetector.detect_distribution()
        self.supported_commands = {
            'centos': {
                'update': 'yum update -y',
                'install': 'yum install -y',
                'firewall': {
                    'stop': 'systemctl stop firewalld',
                    'disable': 'systemctl disable firewalld'
                }
            },
            'ubuntu': {
                'update': 'apt-get update -y',
                'install': 'apt-get install -y',
                'firewall': {
                    'stop': 'systemctl stop ufw',
                    'disable': 'systemctl disable ufw'
                }
            },
            'debian': {
                'update': 'apt-get update -y',
                'install': 'apt-get install -y',
                'firewall': {
                    'stop': 'systemctl stop ufw',
                    'disable': 'systemctl disable ufw'
                }
            },
            'almalinux': {
                'update': 'dnf update -y',
                'install': 'dnf install -y',
                'firewall': {
                    'stop': 'systemctl stop firewalld',
                    'disable': 'systemctl disable firewalld'
                }
            }
        }

    def run_command(self, command: str) -> bool:
        """
        执行系统命令
        
        Args:
            command (str): 要执行的命令
            
        Returns:
            bool: 命令执行是否成功
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"命令执行失败: {e}")
            return False

    def configure_firewall(self) -> bool:
        """
        配置防火墙
        
        Returns:
            bool: 配置是否成功
        """
        if self.dist_info['name'] not in self.supported_commands:
            print(f"不支持的发行版: {self.dist_info['name']}")
            return False

        commands = self.supported_commands[self.dist_info['name']]['firewall']
        success = True
        
        for cmd in commands.values():
            if not self.run_command(cmd):
                success = False
                break
        
        return success

    def update_system(self) -> bool:
        """
        更新系统
        
        Returns:
            bool: 更新是否成功
        """
        if self.dist_info['name'] not in self.supported_commands:
            return False

        update_cmd = self.supported_commands[self.dist_info['name']]['update']
        return self.run_command(update_cmd)

    def configure_network(self, interface: str, ip: str, netmask: str, gateway: str) -> bool:
        """
        配置网络接口
        
        Args:
            interface (str): 网络接口名称
            ip (str): IP地址
            netmask (str): 子网掩码
            gateway (str): 网关地址
            
        Returns:
            bool: 配置是否成功
        """
        if self.dist_info['name'] in ['centos', 'almalinux']:
            config_file = f"/etc/sysconfig/network-scripts/ifcfg-{interface}"
            config = f"""DEVICE={interface}
BOOTPROTO=static
ONBOOT=yes
IPADDR={ip}
NETMASK={netmask}
GATEWAY={gateway}
"""
        else:  # Ubuntu/Debian
            config_file = f"/etc/network/interfaces.d/{interface}"
            config = f"""auto {interface}
iface {interface} inet static
    address {ip}
    netmask {netmask}
    gateway {gateway}
"""

        try:
            with open(config_file, 'w') as f:
                f.write(config)
            return True
        except Exception as e:
            print(f"网络配置失败: {e}")
            return False

    def install_packages(self, packages: list) -> bool:
        """
        安装软件包
        
        Args:
            packages (list): 要安装的软件包列表
            
        Returns:
            bool: 安装是否成功
        """
        if self.dist_info['name'] not in self.supported_commands:
            return False

        install_cmd = self.supported_commands[self.dist_info['name']]['install']
        package_list = ' '.join(packages)
        return self.run_command(f"{install_cmd} {package_list}") 