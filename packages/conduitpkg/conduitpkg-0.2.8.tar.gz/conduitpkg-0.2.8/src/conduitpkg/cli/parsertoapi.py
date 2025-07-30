# SPDX-FileCopyrightText: 2025-present Guille on a Raspberry pi <guilleleiratemes@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
from ..api import advanced

def main():
    if len(sys.argv) < 2:
        sys.argv.append("help")
    local=False
    if "--local" in sys.argv:
        local = True
        sys.argv.remove("--local")
    if sys.argv[1]=="run":
        advanced.run_entry(sys.argv[2], local)
    elif sys.argv[1]=="get":
        if sys.argv[2]=="repos":
            repos=advanced.get_repos(local)
            for repo in repos:
                print(f"[+] Repo: {repo} [+]")
        elif sys.argv[2]=="pkg":
            advanced.install_pkg(sys.argv[3], local)
    elif sys.argv[1]=="post_install":
        if local:
            local=False
        else:
            local=True
        advanced.post_install(local)
    elif sys.argv[1]=="init":
        advanced.init_pkg(sys.argv[2])
    elif sys.argv[1]=="repo":
        if sys.argv[2]=="add":
            advanced.add_repo(sys.argv[3], local)
        elif sys.argv[2]=="remove":
            advanced.remove_repo(sys.argv[3], local)
    elif sys.argv[1]=="compress":
        advanced.compress(sys.argv[2])
    elif sys.argv[1]=="extract":
        advanced.extract(sys.argv[2], local)
    elif sys.argv[1]=="uninstall":
        advanced.uninstall_pkg(sys.argv[2], local)
    elif sys.argv[1]=="info":
        advanced.print_pkg_info(sys.argv[2], local)
    elif sys.argv[1]=="list":
        advanced.list_pkgs(local)
    elif sys.argv[1]=="help":
        print("[+] ----- Help Message ----- [+]")
        print("[*] run                      [*]")
        print("[*] get repos                [*]")
        print("[*] get pkg                  [*]")
        print("[*] post_install             [*]")
        print("[*] init                     [*]")
        print("[*] repo add                 [*]")
        print("[*] repo remove              [*]")
        print("[*] compress                 [*]")
        print("[*] extract                  [*]")
        print("[*] uninstall                [*]")
        print("[*] help                     [*]")
        print("[*] info                     [*]")
        print("[+] --- Help Message End --- [+]")
    else:
        print("[!] Command Not Found    [!]")
        print("[*] Try with 'cpkg help' [*]")
