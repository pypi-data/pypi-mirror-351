#!/usr/bin/env python3
# encoding: utf-8
# @author: firstelfin
# @time: 2025/05/26 20:53:27

import os
import sys
import warnings
import tempfile
import subprocess
from pathlib import Path
warnings.filterwarnings('ignore')
FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # project root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH

from prettytable import PrettyTable
from elfinTerminal.tools.pathSearch import get_apt_conf_path, get_apt_env
from elfinTerminal.source.config import APT_SOURCES


def set_up_apt():

    # 限制操作系统为ubuntu
    exec_status = input("请确认当前系统需要配置apt源, 是否继续? (y/n): ")
    if exec_status.lower() != 'y':
        print("操作已取消")
        return None
    
    apt_conf_path = get_apt_conf_path()

    apt_table = PrettyTable()
    apt_table.field_names = ["序号", "名称", "源地址"]
    for i, (name, url) in enumerate(APT_SOURCES.items()):
        apt_table.add_row([i, name, url])
    print(apt_table)
    choice = input("请选择要使用的有效源(输入序号): ")
    assert choice.isdigit() and 0 <= int(choice) < len(APT_SOURCES), "输入有误，请重新输入"
    choice = int(choice)
    name, url = list(APT_SOURCES.items())[choice]
    print(f"正在设置 {name} 源...")
    system_sep = os.linesep
    version_codename = get_apt_env(['VERSION_CODENAME'])['VERSION_CODENAME']

    new_content = [
        f"deb {APT_SOURCES[name]} {version_codename} main restricted universe multiverse",
        f"deb {APT_SOURCES[name]} {version_codename}-updates main restricted universe multiverse",
        f"deb {APT_SOURCES[name]} {version_codename}-security main restricted universe multiverse",
        f"deb {APT_SOURCES[name]} {version_codename}-proposed main restricted universe multiverse",
        f"deb {APT_SOURCES[name]} {version_codename}-backports main restricted universe multiverse",
        f"deb-src {APT_SOURCES[name]} {version_codename} main restricted universe multiverse",
        f"deb-src {APT_SOURCES[name]} {version_codename}-security main restricted universe multiverse",
        f"deb-src {APT_SOURCES[name]} {version_codename}-updates main restricted universe multiverse",
        f"deb-src {APT_SOURCES[name]} {version_codename}-proposed main restricted universe multiverse",
        f"deb-src {APT_SOURCES[name]} {version_codename}-backports main restricted universe multiverse",
    ]
    
    # 写入new_content到文件
    # 创建临时文件
    with tempfile.NamedTemporaryFile('w', delete=False) as tmp:
        tmp.write(system_sep.join(new_content))
        tmp_path = tmp.name
    try:
        subprocess.run(['sudo', 'mv', tmp_path, str(apt_conf_path)], check=True)
        print(f"设置源成功: {name} 源地址为 {url}")
    except Exception as e:
        print(f"设置源失败: {e}")
        Path(tmp_path).unlink(missing_ok=True)
    subprocess.run(['sudo', 'apt-get', 'update'], check=True)
    print("更新apt源成功")
