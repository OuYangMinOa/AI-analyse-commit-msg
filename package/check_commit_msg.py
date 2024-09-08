#!/usr/bin/python
# -*- coding: utf-8 -*-
import os



from ttkbootstrap.dialogs import Messagebox 
from colorama             import Fore, Back, Style

import subprocess
import datetime     as dt
import sys
import io
import os

from core.AIEditor        import AISuggestEditor
from config               import logger, PASS, FAIL, INTERNAL


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main() -> int:
    ## Find commit message file path
    commit_msg_filepath = ".git//COMMIT_EDITMSG"
    if (os.path.exists(commit_msg_filepath)):
        with open(commit_msg_filepath, 'r', encoding='utf-8') as commit_msg_file:
            commit_msg = commit_msg_file.read()
    else:
        commit_msg = "test"

    win    = AISuggestEditor()

    logger.info(f"[*] Commit message: {commit_msg}")

    ## Ask user if they want to use AI to analyze commit.
    git_show_output = subprocess.check_output(["git", "diff", "--cached"], encoding='utf-8')# , errors='ignore')
    # logger.info(f"[*] Git show output: {git_show_output}")

    result = Messagebox.yesnocancel(f"將會使用AI分析commit\n是否要進行此操作？",title="IGS pre-commit hook tool",parent=win.root, pos="center")
    if (result=="No"):
        print("\n[*] 使用者選擇不使用AI, 直接commit")
        print(f"\n {Back.BLUE}{Fore.YELLOW}Commit without using AI{Style.RESET_ALL}\n")
        win.destroy()
        return PASS

    if (result=="Cancel" or result is None):
        print("\n[*] 使用者取消")
        print(f"\n {Back.RED}{Fore.YELLOW}Cancel{Style.RESET_ALL}\n")
        win.destroy()
        return FAIL

    win.call_openai_with_loading_dialog( git_show_output, commit_msg)
    output = win.openai_result

    suggest_commit_log = output.split('```')[-2].strip() if "```" in output else output
    logger.info("[*] AI suggest commit log:")
    logger.info(output)
    return win.build_widget(output, suggest_commit_log,commit_msg,commit_msg_filepath).start()

if __name__ == '__main__':
    raise SystemExit(main())
