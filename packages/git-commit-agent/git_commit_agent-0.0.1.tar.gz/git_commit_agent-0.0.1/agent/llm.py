from openai import OpenAI
import os

API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_ENDPOINT=os.environ.get("OPENAI_ENDPOINT")
USE_MODEL=os.environ.get("USE_MODEL")

print(API_KEY, OPENAI_ENDPOINT, USE_MODEL)

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=API_KEY,
    base_url=OPENAI_ENDPOINT,
)

def ai(messages: list[dict]):
    completion = client.chat.completions.create(
        model=USE_MODEL,
        # extra_body={"enable_thinking": True},
        messages=messages,  # type: ignore
        stream=True,
    )

    reasoning_content = ""
    answer_content = ""
    is_answering = False

    for chunk in completion:
        if not chunk.choices:
            print("\nUsage:")
        else:
            delta = chunk.choices[0].delta
            # 打印思考过程
            if hasattr(delta, "reasoning_content") and delta.reasoning_content != None:
                reasoning_content += delta.reasoning_content
                # print(delta.reasoning_content, end="")
            else:
                # 开始回复
                if delta.content != "" and is_answering is False:
                    is_answering = True
                answer_content += delta.content
                # print(delta.content, end="")

    result_without_think = answer_content.find("</think>")
    if result_without_think != -1:
        answer_content = answer_content[result_without_think + len("</think>") :]
    return answer_content
