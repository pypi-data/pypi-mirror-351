#  ____       _____           _
# |  _ \ _   |_   _|__   ___ | |___ ____
# | |_) | | | || |/ _ \ / _ \| / __|_  /
# |  __/| |_| || | (_) | (_) | \__ \/ /
# |_|    \__, ||_|\___/ \___/|_|___/___|
#        |___/

# Copyright (c) 2024 Sidney Zhang <zly@lyzhang.me>
# PyToolsz is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#          http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.


import pytoolsz.utils as utils

__version__ = "0.1.1"

def version(println:bool = True, 
            output:bool = False) -> str|None:
    version_txt = [
        "0.1.1 (2025-05-30 LINUX)",
        "Copyright (c) 2024 Sidney Zhang <zly@lyzhang.me>",
        "PyToolsz is licensed under Mulan PSL v2."
    ]
    if println :
        print("\n".join(version_txt))
    if output :
        return "\n".join(version_txt)

__all__ = [
    "utils",
    "version"
]

if __name__ == "__main__":
    version()