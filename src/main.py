#!/usr/bin/env python3
import argparse
from rich.console import Console
from rich.prompt import Prompt
from .system_detector import SystemDetector
from .system_initializer import SystemInitializer

console = Console()

def main():
    # 检查系统是否受支持
    if not SystemDetector.is_supported_distribution():
        console.print("[red]错误：当前系统不受支持！[/red]")
        return

    # 初始化系统初始化器
    initializer = SystemInitializer()
    dist_info = SystemDetector.detect_distribution()
    
    console.print(f"[green]检测到系统: {dist_info['name']} {dist_info['version']}[/green]")
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='系统初始化工具')
    parser.add_argument('--auto', action='store_true', help='自动模式，使用默认配置')
    args = parser.parse_args()

    if args.auto:
        # 自动模式
        console.print("[yellow]运行自动模式...[/yellow]")
        
        # 配置防火墙
        console.print("[cyan]配置防火墙...[/cyan]")
        if initializer.configure_firewall():
            console.print("[green]防火墙配置成功[/green]")
        else:
            console.print("[red]防火墙配置失败[/red]")
        
        # 更新系统
        console.print("[cyan]更新系统...[/cyan]")
        if initializer.update_system():
            console.print("[green]系统更新成功[/green]")
        else:
            console.print("[red]系统更新失败[/red]")
    else:
        # 交互模式
        console.print("[yellow]运行交互模式...[/yellow]")
        
        # 配置防火墙
        if Prompt.ask("是否配置防火墙？", choices=["y", "n"]) == "y":
            console.print("[cyan]配置防火墙...[/cyan]")
            if initializer.configure_firewall():
                console.print("[green]防火墙配置成功[/green]")
            else:
                console.print("[red]防火墙配置失败[/red]")
        
        # 更新系统
        if Prompt.ask("是否更新系统？", choices=["y", "n"]) == "y":
            console.print("[cyan]更新系统...[/cyan]")
            if initializer.update_system():
                console.print("[green]系统更新成功[/green]")
            else:
                console.print("[red]系统更新失败[/red]")
        
        # 配置网络
        if Prompt.ask("是否配置网络？", choices=["y", "n"]) == "y":
            interface = Prompt.ask("请输入网络接口名称")
            ip = Prompt.ask("请输入IP地址")
            netmask = Prompt.ask("请输入子网掩码")
            gateway = Prompt.ask("请输入网关地址")
            
            console.print("[cyan]配置网络...[/cyan]")
            if initializer.configure_network(interface, ip, netmask, gateway):
                console.print("[green]网络配置成功[/green]")
            else:
                console.print("[red]网络配置失败[/red]")
        
        # 安装软件包
        if Prompt.ask("是否安装基础软件包？", choices=["y", "n"]) == "y":
            packages = Prompt.ask("请输入要安装的软件包（用空格分隔）").split()
            console.print("[cyan]安装软件包...[/cyan]")
            if initializer.install_packages(packages):
                console.print("[green]软件包安装成功[/green]")
            else:
                console.print("[red]软件包安装失败[/red]")

if __name__ == "__main__":
    main() 