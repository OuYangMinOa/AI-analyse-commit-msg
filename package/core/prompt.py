
from config import MAX_PROMPT_LEN
from tqdm   import tqdm


### Custom your own AI here.
def prompt(message):
    import requests
    prompt = {
        "promptWord":message[1]["content"],
        "top_p":0.2,
        "temperature":0.3,
        "system_prompt" : message[0]["content"], 
        }
    response  = requests.post(f"http://127.0.0.1:8088/prompt",json=prompt)
    reJson = response.json()
    print(reJson)
    if (reJson["status"] =="ok"):
        return reJson["data"]["ouput"]



def call_openai2(text:str, commit_log:str) -> str:
    all_result = "Summary Source\n=====\n"
    for i in tqdm(range( len(text)//MAX_PROMPT_LEN )):
        this_text = text[i*MAX_PROMPT_LEN:(i+1)*MAX_PROMPT_LEN]
        response = prompt( build_sub_prompt(this_text) )
        all_result +=f"memory {i+1}:\n{response}"
    return all_result + analyze_diff_with_openai(all_result, commit_log)
            

def analyze_diff_with_openai( commit:str, commit_log:str) -> str:
    response = prompt( build_prompt(commit, commit_log) )
    return response



def build_sub_prompt(text:str):
    output = [
                {"role": "system", "content": "你是一個git版本的分析專家，擅長追蹤commit的變化。"},
                {"role": "user",
                "content":(
                "以下是此次commit變更一部分，請理解這部分程式碼之間的調度關係，是否有inherence等...,"
                "以及使用者在這次commit做了那些變更。\n"
                f"commit:\n{text}\n"
                "請簡短把以上程式碼總結後，做成記憶，方便與之後 commit變更的記憶一起生成新的commit log。\n"
                "記憶:"
                )
                }]
    return output

def build_prompt(commit:str, commit_log:str):
    output = [
            {"role": "system", "content": "你是一個git版本的分析專家，擅長追蹤commit的變化。"},
            {"role": "user",
             "content":(
             "請分析這次commit的變更以及其commit log，理解程式碼之間的調度關係，是否有inherence等...,"
             "以及使用者在這次commit做了那些變更，並以以上內容提供目的，摘要，以及優化建議，"
             "優化建議要包含檔案名、此檔案的變動摘要以及此檔案優化的方向與其原因。\n"
             "最後，檢視以上的內容是否跟他提供的commit log一致，若不一致，請提供建議跟合適的commit log。\n"
             "commit log 需要符合以下格式:\n"
             "'''\n"
             "TYPE: SUBJECT\n\n"
             "BODY\n\n"
             "FOOTER\n"
             "```\n"
             "一個完整的Commit訊息必須包含以上三大區塊，且都由空行區隔。第一行標題列，必須包含TYPE與BODY。"
             "TYPE必須包含在標題中，且符合下列類型。\n"
             "feat: 新增/修改功能 (feature)。\n"
             "fix: 修補 bug (bug fix)。\n"
             "docs: 文件 (documentation)。\n"
             "style: 格式 (不影響程式碼運行的變動)。\n"
             "refactor: 重構 (既不是新增功能，也不是修補 bug 的程式碼變動)。\n"
             "perf: 改善效能。\n"
             "test: 增加測試。\n"
             "chore: 建構程序或輔助工具的變動 (maintain)。\n"
             "revert: 撤銷回覆先前的 commit 例如：revert: type(scope): subject (回覆版本：xxxx)。\n"
             "SUBJECT :\n"
             "SUBJECT 不應超過50個字元，言簡意賅的簡述此Commit的改動。\n"
             "BODY:\n"
             "撰寫BODY時，請務必將改了什麼與為什麼而改以及可能造成的副作用寫清楚。"
             "每行不超過72個字。\n"
             "FOOTER:\n"
             "如果使用者有標註對應的issue編號(issue tracker IDs)"
             "才需要FOOTER，不然一律留空!!"
             "輸出內容格式"
             "===== \n"
             "目的:\n"
             "提交的摘要:\n"
             "提交內容優化建議:\n"
             "1. 檔案名稱:`<檔案名稱>`\n"     
             "   變動摘要: <摘要>\n"
             "   優化建議:\n"
             "   - <優化的建議1，如果可以直接提供範例會更好>\n"
             "   - <優化的建議2，如果可以直接提供範例會更好>\n\n"
             "\n===== \n\n"
             "Commit log:\n"
             "    建議: <對使用者輸入的commit log提供建議，並說明你的理由。>\n"
             "    New commit log:\n"
             "    ```\n"
             "    <根據建議使用中文提供適合此次更新的commit log>\n" 
             "    ```\n"
             "\n===== \n"
             f"commit:\n{commit}\n"
             f"commit log:{commit_log}\n"
            )
            }
        ]
    return output

