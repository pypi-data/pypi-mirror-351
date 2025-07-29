#!/usr/bin/env python3
# encoding: utf-8
# @author: firstelfin
# @time: 2025/05/21 22:36:27

import os
import re
import sys
import subprocess
import warnings
from pathlib import Path
warnings.filterwarnings('ignore')
FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # project root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH


def get_pip_conf_path():
    """获取pip配置文件路径"""

    new_path = (Path.home() / '.config' / 'pip' / 'pip.conf').expanduser()
    if new_path.exists():
        return new_path
    else:
        new_path = (Path.home() / '.pip' / 'pip.conf').expanduser()
        return new_path


def get_pypi_conf_path():
    """获取PyPI配置文件路径"""
    
    new_path = (Path.home() / '.pypirc').expanduser()
    return new_path


def get_vim_conf_path():
    """获取Vim配置文件路径"""

    new_path = (Path.home() / ".vimrc").expanduser()
    return new_path


def get_apt_conf_path():
    """获取Apt配置文件路径"""
    apt_source_list = Path("/etc/apt/sources.list")
    # 生成bak文件
    bak_file = Path("/etc/apt/sources.list.elfinBak")
    if not bak_file.exists() and apt_source_list.exists():
        subprocess.run(['sudo', 'cp', str(apt_source_list), str(bak_file)], check=True)
        print(f"Apt配置文件已经备份到: {bak_file}")
    
    return apt_source_list


def get_apt_env(env_list: list) -> dict:
    """获取Apt环境变量"""
    
    env_list = [env_list] if isinstance(env_list, str) else env_list
    apt_env = {key: None for key in env_list}

    with open('/etc/os-release', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # 匹配 KEY=VAL 或 KEY="VAL" 格式
                match = re.match(r'^([A-Z_]+)=(?:"(.*)"|(.*))$', line)
                if match:
                    key = match.group(1)
                    val = match.group(2) or match.group(3)
                    if key not in apt_env:
                        continue
                    apt_env[key] = val
    return apt_env
