#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
"""
功 能：buildgppbin脚本，该脚本 make pme jffs2 cramfs gpp bin image
版权信息：华为技术有限公司，版本所有(C) 2019-2020
"""

import os
import re
import shutil

from bmcgo.tasks.task import Task
from bmcgo import errors
from bmcgo import misc


class TaskClass(Task):
    def copy_files(self):
        # 复制gpp需要使用的文件,记录rootfs.img、rootfs.img.cms、cms.crl、rootca.der、Hi1711_boot_4096.bin、Hi1711_boot_pmode.bin共六个文件
        files = self.get_manufacture_config(f"gpp/files")
        if files is None:
            raise errors.BmcGoException("获取 manifest.yml 中 gpp 配置失败, 退出码: -1")
        # 复制构建emmc gpp镜像所需的文件
        self.copy_manifest_files(files)

    def copy_gpp_headers_files(self):
        files = self.get_manufacture_config(f"gpp/pkg_headers")
        if files is None:
            if self.config.chip != "1711":
                raise errors.BmcGoException("获取 manifest.yml 中 gpp/pkg_headers 配置失败, 退出码: -1")
            else:
                files = []
                files.append({"file": "/usr/local/bin/hpm_header.config", "dst": "hpm_header.config"})
        self.copy_manifest_files(files)

    def build_gpp_hpm_bin(self):
        self.info("构建 gpp 二进制文件")
        self.chdir(self.config.hpm_build_dir)
        self.copy_files()
        self.copy_gpp_headers_files()

        # 复制cms.crl
        self.run_command("gpp_header hpm")

        if not os.path.exists("hpm_top_header"):
            raise errors.BmcGoException(f"hpm_top_header 不存在 ! 创建 hpm_sub_header 失败!")

        if not os.path.exists("hpm_sub_header"):
            raise errors.BmcGoException(f"hpm_sub_header 不存在 ! 创建 hpm_sub_header 失败!")

        if self.config.chip == "1711":
            pmode_file = "Hi1711_boot_pmode.bin "
        else:
            pmode_file = ""


        self.info(f"打包: {self.config.board_name}_gpp.bin")
        cmd = f"ls -al hpm_top_header Hi1711_boot_4096.bin {pmode_file}"
        cmd += "hpm_sub_header rootca.der rootfs_BMC.img.cms cms.crl rootfs_BMC.tar.gz"
        self.run_command(cmd, show_log=True)

        target_path = f"{self.config.work_out}/{self.config.board_name}_gpp.bin"
        cmd = f"cat hpm_top_header Hi1711_boot_4096.bin {pmode_file}"
        cmd += "hpm_sub_header rootca.der rootfs_BMC.img.cms cms.crl rootfs_BMC.tar.gz"
        self.info("执行命令: " + cmd)
        self.pipe_command([cmd], target_path)

    def run(self):
        self._move_dependency()
        self.build_gpp_hpm_bin()
        self.info(f"目录 {self.config.work_out} 包含文件:\n{os.listdir(self.config.work_out)}")

    def _move_dependency(self):
        # 移动到tools/build_tools目录中
        self.chdir(self.config.sdk_path)
        if self.config.chip == "1711":
            self.run_command(f"dd if=Hi1711_boot_4096_pmode.bin of=Hi1711_boot_pmode.bin bs=1k count=1024 skip=768")
            self.run_command(f"dd if=Hi1711_boot_4096_pmode_debug.bin of=Hi1711_boot_pmode_debug.bin bs=1k " +
                            "count=1024 skip=768")
