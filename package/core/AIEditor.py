
from ttkbootstrap.dialogs import Messagebox 
from colorama             import Back, Fore, Style

import ttkbootstrap as tk
import threading
import datetime     as dt
import requests     as re
import ctypes       as ct
import os

from config         import VERSION, PASS, FAIL, INTERNAL, logger, MAX_PROMPT_LEN
from .prompt        import call_openai2, analyze_diff_with_openai


def dark_title_bar(window):
    """Dark title bar for Windows"""
    window.update()
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ct.windll.user32.GetParent
    hwnd = get_parent(window.winfo_id())
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 2
    value = ct.c_int(value)
    set_window_attribute(hwnd, rendering_policy, ct.byref(value),
                        ct.sizeof(value))
    

class AISuggestEditor:
    def __init__(self,):
        self.root = tk.Window(themename="darkly")
        self.root.title(f'commit-checker {VERSION}')
        self.root.wm_attributes("-topmost", 1)
        self.root.resizable(True, True)
        self.root.overrideredirect(1)
        self.root.geometry('1x1+900+500') # width x height

    def call_openai_with_loading_dialog(self, text:str, commit_log:str) -> str:
        self.loading_window = None
        threading.Thread(target=self._call_openai, args=(text, commit_log)).start()
        self.show_waiting_dialog()
    
    def _call_openai(self, text:str, commit_log:str) -> str:
        try:
            if (len(text) > MAX_PROMPT_LEN):
                logger.info(f"[*] Text is too long({len(text)}), split it into {MAX_PROMPT_LEN} characters each.")
                self.openai_result = call_openai2(text, commit_log)
            else:
                self.openai_result = analyze_diff_with_openai(text, commit_log)
        except Exception as e:
            print(f"[*] 錯誤:")
            logger.error(f"[*] __call_openai : {e}")
            logger.error(f"[*] __call_openai : {e.__traceback__}")
            raise SystemExit(FAIL)


        self.close_waiting_dialog()

    def show_waiting_dialog(self):
        self.loading_window = LoadingWindows(self.root)
        self.root.mainloop()
        
    def close_waiting_dialog(self):
        try:
            self.loading_window.destroy()
        except:
            pass
        self.root.quit()

    def build_widget(self, output:str, suggest_commit_log:str, origin_commit_log:str,commit_msg_filepath:str):
        self.root.overrideredirect(False)
        self.root.geometry('1000x910+460+0') # width x height
        self.output  = output
        self.IF_PASS = FAIL 
        self.suggest_commit_log  = suggest_commit_log
        self.origin_commit_log   = origin_commit_log
        self.commit_msg_filepath = commit_msg_filepath

        for i in range(6):
            self.root.columnconfigure(i, weight=1)
            self.root.rowconfigure(i, weight=1)

        try:
            dark_title_bar(self.root)
        except:
            pass

        mylabel = tk.Label(self.root, text='AI的建議', font=('Helvetica', 30, 'bold'),justify='left')
        mylabel.grid(row=0, column=0, columnspan=6, padx=10, pady=10)


        ### AI suggestion
        mylabel = tk.Text(self.root, font=('Helvetica',12), height=10)
        mylabel.insert('0.0', output+"\n"*5)
        mylabel.grid(row=1, column=0, columnspan=6,sticky='nswe', padx=10)
        mylabel.see("end")  

        scrollb = tk.Scrollbar(self.root, command=mylabel.yview)
        mylabel['yscrollcommand'] = scrollb.set
        scrollb.grid(row=1, column=5, sticky='nse', padx=10)

        #####################

        mylabel = tk.Label(self.root, font=('Helvetica', 15, 'bold'), text='編輯AI給你的commit建議',justify='left')
        mylabel.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

        mylabel = tk.Label(self.root, font=('Helvetica', 15, 'bold'), text='你原本的commit',justify='left')
        mylabel.grid(row=2, column=3, columnspan=3, padx=10, pady=10)

        
        ## AI suggest commit log
        self.myentry = tk.Text(self.root, font=('Helvetica',12), height=6)
        self.myentry.insert('0.0', suggest_commit_log+"\n"*5)
        self.myentry.grid(row=3, column=0, columnspan=3, sticky="nsw", padx=10)

        scrollb2 = tk.Scrollbar(self.root, command=self.myentry.yview)
        self.myentry['yscrollcommand'] = scrollb2.set
        scrollb2.grid(row=3, column=2, sticky='nse', padx=10)


        ## Original commit log
        self.myentry1 = tk.Text(self.root, font=('Helvetica',12), height=6)
        self.myentry1.insert('0.0', origin_commit_log+"\n"*5)
        self.myentry1.grid(row=3, column=3, columnspan=3, sticky="nssw", padx=10)

        scrollb2 = tk.Scrollbar(self.root, command=self.myentry1.yview)
        self.myentry1['yscrollcommand'] = scrollb2.set
        scrollb2.grid(row=3, column=5, sticky='nse', padx=10)

        
        mybutton = tk.Button(self.root, text='Commit', command=self.AI_commit, width=18)
        mybutton.grid(row=4, column=0, columnspan=2, padx=10, pady=15)

        origin_button = tk.Button(self.root, text='用原本的', command=self.origin_commit, width=18)
        origin_button.grid(row=4, column=2, columnspan=2, padx=10, pady=15)

        cancel_button = tk.Button(self.root, text='取消', command=self.cancel_commit, width=18)
        cancel_button.grid(row=4, column=4, columnspan=2, padx=10, pady=15,)

        return self
    
    def destroy(self):
        self.root.destroy()

    def start(self):
        self.root.mainloop()
        return self.IF_PASS
    
    def AI_commit(self):
        user_input = self.myentry.get("0.0", "end").strip()
        result = Messagebox.okcancel(f"將會使用編輯後的AI commit log\n{user_input}\n確認要進行此操作嗎？",parent=self.root)
        if (result=="Cancel" or result is None):
            return

        with open(self.commit_msg_filepath, 'w', encoding='utf-8') as commit_msg_file:
            commit_msg_file.write(user_input)
        self.IF_PASS = PASS
        print(f"\n[*] 編輯的AI commmit log\n\n```\n{user_input}\n```")
        print(f"\n {Back.GREEN}{Fore.BLACK}Commit AI suggested{Style.RESET_ALL}")
        self.root.destroy()

    def origin_commit(self):
        user_input = self.myentry1.get("0.0", "end").strip()

        result = Messagebox.okcancel(f"將會使用原本的commit log\n{user_input}\n確認要進行此操作嗎？",parent=self.root, pos="center")
        print(result)
        if (result=="Cancel" or result is None):
            return
        
        with open(self.commit_msg_filepath, 'w', encoding='utf-8') as commit_msg_file:
            commit_msg_file.write(user_input)

        self.IF_PASS = PASS
        print(f"\n[*] 使用原本的commit log\n\n```\n{user_input}\n```")
        print(f"\n {Back.BLUE}{Fore.YELLOW}No Change{Style.RESET_ALL}")
        self.root.destroy()

    def cancel_commit(self):
        result = Messagebox.okcancel("將會取消 commit\n確認要進行此操作嗎？",parent=self.root, pos="center" ,geometry='center')
        if (result=="Cancel" or result is None):
            return
        self.IF_PASS = FAIL
        print(f"\n[*] 取消 commit")
        print(f"\n {Back.RED}{Fore.YELLOW}Cancel{Style.RESET_ALL}")
        self.root.destroy()




    
class LoadingWindows(tk.Toplevel):
    def __init__(self,master):
        super().__init__(self,master)
        self.master = master
        self.title('Waiting for OpenAI')
        self.protocol("WM_DELETE_WINDOW", self.callback)
        self.frameCnt = 12

        loading_gif_floder = INTERNAL
        loading_gif = os.path.join(loading_gif_floder, "loading.gif")

        self.frames = [tk.PhotoImage(file=loading_gif,format = 'gif -index %i' %(i)) for i in range(self.frameCnt)]
        
        self.resizable(False,False)
        self.loading_label = tk.Label(self)
        self.loading_label.pack()
        self.after(100, self.update_loading_dialog, 0)
        
    def update_loading_dialog(self,ind):
        frame = self.frames[ind]
        ind += 1
        if ind == self.frameCnt:
            ind = 0
        try:
            self.loading_label.configure(image=frame)
            self.after(100, self.update_loading_dialog, ind)
        except:
            pass

    def callback(self): 
        result = Messagebox.okcancel(f"是否要取消 prompt?",parent=self)
        if (result=="Cancel" or result is None):
            return
    
        else:
            logger.info(f"\n[*] 取消 prompt")
            print(f"\n {Back.RED}{Fore.YELLOW}Cancel{Style.RESET_ALL}")
            self.destroy()
            raise SystemExit(FAIL)


