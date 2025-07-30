import sys
import subprocess

from dotenv import load_dotenv
load_dotenv()

from agent.llm import ai

def commit():
    args = sys.argv[1:]

    # 执行 git add
    result1 = subprocess.call(["git", "add", *args])
    print(result1)

    # 获取diff
    result2 = subprocess.Popen(
        ['git', 'diff', '--staged'],
        stdout=subprocess.PIPE,
        encoding='utf-8'
    )
    output = result2.stdout.read()

    # 使用大模型获取commit信息
    system_prompt = """
        You are a commit message generator, if user not provide the ragulation of commit message, make a commit message with the following rules:
        
        1. The commit message should be in English.
        2. The commit message should be concise and clear.
  
    """
    
    user_prompt = """
        Please generate a commit message for the following diff:
        
        {diff}
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt.format(diff=output)},
    ]

    result3 = ai(messages)
    print(result3)

    # 让用户确认
    # print("Please confirm the commit message above. 确认上述提交信息")
    x = input('确认上述提交信息? [y/n] ')
    if x != 'y':
        print("Aborted.")
        return

    # 执行 git commit
    result4 = subprocess.call(["git", "commit", "-m", result3])
    print(result4)
    
    # 判断是否是 main 或者 master 分支， 如果是则不能推送到远程仓库
    current_branch = subprocess.check_output(["git", "branch", "--show-current"]).decode("utf-8").strip()
    if current_branch == "main" or current_branch == "master":
        print("main or master branch, cannot push to remote repository. 不能推送到远程仓库")
        return
    
    # 让用户确认是否push
    print("Push to remote repository? 确认是否推送到远程仓库")
    x = input('确认是否推送到远程仓库? [y/n] ')
    if x != 'y':
        print("Aborted.")
        return

    # 执行 git push
    result5 = subprocess.call(["git", "push"])
    print(result5)