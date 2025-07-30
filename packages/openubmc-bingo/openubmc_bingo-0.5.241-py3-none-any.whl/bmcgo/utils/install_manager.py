#!/usr/bin/env python3
# encoding=utf-8
# 描述：安装管理器
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

from pathlib import Path
from bmcgo.utils.tools import Logger
from bmcgo.utils.installations import install_consts
from bmcgo.utils.installations.install_workflow import InstallWorkflow
from bmcgo.utils.installations.base_installer import BaseInstaller

logger = Logger(name="upgrade", log_file="/usr/share/bmcgo/install.log")
InstallWorkflow.logger = logger
BaseInstaller.logger = logger


class InstallManager:
    def __init__(self):
        self._custom_path = None

    @property
    def custom_installer_path(self):
        return self._custom_path / install_consts.PLUGIN_INSTALLER_PATH
    
    @property
    def custom_install_plan_path(self):
        return self._custom_path / install_consts.PLUGIN_INSTALL_PLAN_PATH

    def install(self, app_name, operator, version, custom_path):
        self._set_custom_path(custom_path)
        BaseInstaller.discover_installers()
        InstallWorkflow.discover_workflows()

        workflows = []
        if app_name == install_consts.INSTALL_ALL:
            workflows = list(InstallWorkflow.get_all_plans())
        else:
            workflows = [app_name]

        for wname in workflows:
            logger.info(f"安装{wname}...")
            plans = InstallWorkflow.parse(wname)
            for plan in plans.get(install_consts.PLAN_STEPS, []):
                inst_type = plan.get(install_consts.PLAN_INSTALL_TYPE)
                BaseInstaller.get_installer(inst_type).install(plan, operator, version)

    def _set_custom_path(self, custom_path: str):
        self._custom_path = Path(custom_path).resolve()
        if not self._custom_path.exists() or not self._custom_path.is_dir():
            logger.warning(f"无效的地址: {self._custom_path}")
            return
        BaseInstaller.add_installer_dir(self.custom_installer_path)
        InstallWorkflow.add_plan_dir(self.custom_install_plan_path)