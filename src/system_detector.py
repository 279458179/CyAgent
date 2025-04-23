import os
import subprocess
from typing import Dict, Optional

class SystemDetector:
    @staticmethod
    def detect_distribution() -> Dict[str, str]:
        """
        检测Linux发行版信息
        
        Returns:
            Dict[str, str]: 包含发行版名称和版本的字典
        """
        try:
            # 尝试读取/etc/os-release文件
            with open('/etc/os-release', 'r') as f:
                os_release = f.read()
            
            dist_info = {}
            for line in os_release.split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    dist_info[key] = value.strip('"')
            
            return {
                'name': dist_info.get('ID', 'unknown').lower(),
                'version': dist_info.get('VERSION_ID', 'unknown')
            }
        except FileNotFoundError:
            # 如果os-release不存在，尝试其他方法
            try:
                # 检查CentOS/AlmaLinux
                if os.path.exists('/etc/centos-release'):
                    with open('/etc/centos-release', 'r') as f:
                        content = f.read().lower()
                        if 'centos' in content:
                            return {'name': 'centos', 'version': content.split()[3]}
                        elif 'almalinux' in content:
                            return {'name': 'almalinux', 'version': content.split()[3]}
                
                # 检查Ubuntu
                if os.path.exists('/etc/lsb-release'):
                    with open('/etc/lsb-release', 'r') as f:
                        content = f.read()
                        if 'ubuntu' in content.lower():
                            for line in content.split('\n'):
                                if 'DISTRIB_RELEASE' in line:
                                    return {'name': 'ubuntu', 'version': line.split('=')[1]}
                
                # 检查Debian
                if os.path.exists('/etc/debian_version'):
                    with open('/etc/debian_version', 'r') as f:
                        return {'name': 'debian', 'version': f.read().strip()}
                
            except Exception as e:
                print(f"Error detecting distribution: {e}")
        
        return {'name': 'unknown', 'version': 'unknown'}

    @staticmethod
    def is_supported_distribution() -> bool:
        """
        检查当前系统是否受支持
        
        Returns:
            bool: 如果系统受支持返回True，否则返回False
        """
        dist_info = SystemDetector.detect_distribution()
        supported_distros = ['centos', 'ubuntu', 'debian', 'almalinux']
        return dist_info['name'] in supported_distros 