#!/usr/bin/env python3
# encoding=utf-8
# 描述：apt安装工具
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
import os
import base64
import tempfile
import requests
from typing import Dict, List
from pathlib import Path
from bmcgo.utils.tools import Tools
from bmcgo.utils.installations import install_consts
from bmcgo.utils.installations.version_util import PkgVersion
from bmcgo.utils.installations.base_installer import BaseInstaller


tool = Tools("apt_install")


class AptInstaller(BaseInstaller, installer_type="apt"):
    def __init__(self):
        self._repo_url = None
        self._gpg_file = None
        self._config_file = None
        self._repo_public_key = None
        self._pkg_name = None
        self._pkg_version = None

    def install(self, plan: Dict[str, List[str]], operator: str, version: str):
        self._parse_plan(plan)
        self._install_key()

        if not self._check_repo():
            self.logger and self.logger.info("未检测到仓库配置，开始配置")
            self._config_repo()

        self._update_cache()

        target = [self._pkg_name]
        if operator and version:
            ver = self._resolve_constraint(operator, version)
            if ver:
                target.append(ver)
        pkg = "=".join(target)
        self._install_package(pkg)
        self.logger and self.logger.info(f"安装{pkg}完成！")

    def _get_versions(self) -> List[PkgVersion]:
        result = tool.run_command(["apt-cache", "madison", self._pkg_name], capture_output=True)
        if not result.stdout:
            return []
        return [PkgVersion(line.split("|")[1].strip()) for line in result.stdout.splitlines()]
    
    def _resolve_constraint(self, opt: str, ver: str) -> str:
        versions = self._get_versions()
        if not versions:
            self.logger and self.logger.warning("当前没有可下载版本!")
            return None

        if ver == install_consts.INSTALL_LATEST or not opt:
            return versions[0].origin

        pkg_ver = PkgVersion(ver)
        for v in versions:
            if opt == ">=" and v >= pkg_ver:
                return v.origin
            elif opt == "<=" and v <= pkg_ver:
                return v.origin
            elif opt == "!=" and v != pkg_ver:
                return v.origin
            elif opt == "<" and v < pkg_ver:
                return v.origin
            elif opt == ">" and v > pkg_ver:
                return v.origin
            elif opt == "=" and v == pkg_ver:
                return v.origin
            
        raise ValueError(f"没有找到匹配的版本：{opt}{ver}")

    def _parse_plan(self, plan: Dict[str, List[str]]):
        repo_url = plan.get(install_consts.PLAN_REPO_URL)
        repo_public_key = plan.get(install_consts.PLAN_PUBLIC_KEY)
        gpg_file = plan.get(install_consts.PLAN_GPG)
        config_file = plan.get(install_consts.PLAN_CONFIG_FILE)
        pkg_name = plan.get(install_consts.PLAN_PACKAGE_NAME)

        if not all(val for key, val in locals().items() if key not in ["self", "plan"]):
            values = [
                f"{install_consts.PLAN_REPO_URL}: {repo_url}",
                f"{install_consts.PLAN_PUBLIC_KEY}: {repo_public_key}",
                f"{install_consts.PLAN_GPG}: {gpg_file}",
                f"{install_consts.PLAN_CONFIG_FILE}: {config_file}",
                f"{install_consts.PLAN_PACKAGE_NAME}: {pkg_name}"
            ]
            raise ValueError(f"请检查安装配置文件：\n{"\n\t".join(values)}\n")

        self._repo_url = repo_url
        self._repo_public_key = f"{self._repo_url}{repo_public_key}"
        self._gpg_file = Path("/usr/share/keyrings") / gpg_file
        self._config_file = Path("/etc/apt/sources.list.d/") / config_file
        self._pkg_name = pkg_name

    def _install_key(self):
        self.logger and self.logger.info("下载公钥")
        try:
            key_data = requests.get(self._repo_public_key).content
        except Exception as e:
            raise RuntimeError("下载公钥失败")
        
        lines = key_data.splitlines()
        in_block = False
        b64data = []

        for line in lines:
            if line.startswith(b"-----BEGIN PGP"):
                in_block = True
                continue
            if line.startswith(b"-----END PGP"):
                in_block = False
                continue
            if in_block and line.strip() and not line.startswith(b"="):
                b64data.append(line.strip())

        if not b64data:
            raise ValueError("公钥出错")

        dearmor = base64.b64decode(b"".join(b64data))

        with open(self._gpg_file, "wb") as f:
            f.write(dearmor)
        os.chmod(self._gpg_file, 0o644)

    def _check_repo(self):
        if not self._config_file.exists():
            return False
        
        expect_line = f"deb [signed-by={self._gpg_file}] {self._repo_url} stable main\n"
        with open(self._config_file) as f:
            return any(line.strip() == expect_line.strip() for line in f)

    def _config_repo(self):
        repo_line = f"deb [signed-by={self._gpg_file}] {self._repo_url} stable main\n"

        self.logger and self.logger.info("配置仓资源")
        with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
            tmp.write(repo_line)
            tmp_path = tmp.name

        try:
            tool.run_command(["mv", tmp_path, str(self._config_file)], sudo=True)
            tool.run_command(["chmod", "644", str(self._config_file)], sudo=True)
        except Exception as e:
            os.remove(tmp_path)
            raise RuntimeError(f"写入仓库配置失败: {str(e)}")

    def _update_cache(self):
        self.logger and self.logger.info("更新 apt 缓存")
        try:
            tool.run_command(["apt-get", "update"], sudo=True)
        except Exception as e:
            raise RuntimeError(f"安装失败： {str(e)}")
        
    def _install_package(self, pkg: str):
        self.logger and self.logger.info(f"安装: {pkg}")
        try:
            tool.run_command(["apt-get", "install", "-y", "--allow-downgrades", pkg], sudo=True)
        except Exception as e:
            raise RuntimeError(f"安装失败: {str(e)}")
        