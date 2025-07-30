#!/usr/bin/env python3
# encoding=utf-8
# 描述：pip安装工具
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
import sys
import shutil
from typing import Dict, List
from bmcgo.utils.tools import Tools
from bmcgo.utils.installations import install_consts
from bmcgo.utils.installations.base_installer import BaseInstaller


tool = Tools("pip_install")


class PipInstaller(BaseInstaller, installer_type="pip"):
    def install(self, plan: Dict[str, List[str]], operator: str, version: str):
        if operator == "=":
            operator = "=="

        pkg_name = plan.get(install_consts.PLAN_PACKAGE_NAME)
        app_name = plan.get(install_consts.PLAN_MODULE_NAME)

        if version == install_consts.INSTALL_LATEST or not operator:
            pkg_info = pkg_name
        else:
            pkg_info = "".join([pkg_name, operator, version])
        cmds = [sys.executable, "-m", "pip", "install", "--upgrade", pkg_info]
        
        with open("/etc/issue", "r") as fp:
            issue = fp.readline()
            if issue.startswith("Ubuntu 24.04"):
                cmds.append("--break-system-packages")

        self.logger and self.logger.info(f"pip 开始安装{pkg_info}")
        need_sudo = shutil.which(app_name).startswith("/home")
        tool.run_command(cmds, sudo=need_sudo, show_log=True)
        self.logger and self.logger.info(f"pip 安装{pkg_info}完成！")