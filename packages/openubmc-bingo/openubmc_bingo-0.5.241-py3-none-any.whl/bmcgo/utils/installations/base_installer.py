#!/usr/bin/env python3
# encoding=utf-8
# 描述：安装工具工厂类
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
import abc
import sys
import importlib.util
from pathlib import Path
from typing import Dict, List, Type
from bmcgo.utils.installations import install_consts


class BaseInstaller(abc.ABC):
    logger = None
    _intallers: Dict[str, Type["BaseInstaller"]] = {}
    search_paths: List[Path] = [Path(__file__).resolve().parent / install_consts.PLUGIN_INSTALLER_PATH]

    def __init_subclass__(cls, installer_type: str, **kwargs):
        super.__init_subclass__(**kwargs)

        key = installer_type or cls.__name__.lower()
        if key in cls._intallers:
            cls.logger and cls.logger.warning(f"{installer_type}({cls._intallers[key]} 被替换为: {cls})")
        cls._intallers[installer_type] = cls

    @classmethod
    def add_installer_dir(cls, directory: Path):
        if directory not in cls.search_paths:
            cls.search_paths.append(directory)

    @classmethod
    def discover_installers(cls):
        for path in cls.search_paths:
            if not path.exists():
                cls.logger and cls.logger.warning(f"未知安装工具路径：: {str(path)}，跳过")
                continue

            for inst in path.glob("*.py"):
                if inst.name == "__init__.py":
                    continue

                module_name = inst.stem
                spec = importlib.util.spec_from_file_location(f"installer_{module_name}", inst)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    try:
                        sys.modules[module.__name__] = module
                        spec.loader.exec_module(module)
                    except Exception as e:
                        cls.logger and cls.logger.exception(f"加载安装器 {inst} 失败: {str(e)}")
                        continue

    @classmethod
    def get_installer(cls, installer_type: str) -> "BaseInstaller":
        installer_cls = cls._intallers.get(installer_type)
        if not installer_cls:
            raise ValueError(f"未定义的安装方法：{installer_type}")
        return installer_cls()

    @abc.abstractmethod
    def install(self, plan: Dict[str, List[str]], operator: str, version: str):
        """ 安装入口 """