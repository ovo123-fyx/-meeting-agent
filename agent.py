"""会议纪要问答 Agent。

核心是一个循环：
    问模型 -> 模型要调工具 -> 执行工具 -> 把结果塞回去 -> 再问模型
一直到模型不再要工具，直接给出答案为止。
"""

import json
import os

from openai import OpenAI

from tools import TOOL_SCHEMAS, dispatch

MODEL = "deepseek-chat"
MAX_ROUNDS = 5          # 防止模型一直要工具，死循环

SYSTEM_PROMPT = """你是一个会议纪要助手。

规则：
1. 回答之前必须先用工具查会议纪要，不要凭记忆编。
2. 工具查不到就直说查不到，不要猜。
3. 回答里要带上信息来自哪一场会（日期 + 标题）。
4. 回答简短，中文。"""


def make_client():
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        raise SystemExit("没有读到 DEEPSEEK_API_KEY，先在终端 export 一下")
    return OpenAI(api_key=key, base_url="https://api.deepseek.com")


def run(question, verbose=True):
    """跑一次完整的 Agent 循环，返回最终答案。"""
    client = make_client()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    for round_no in range(1, MAX_ROUNDS + 1):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOL_SCHEMAS,
        )
        msg = response.choices[0].message
        messages.append(msg)

        # ---- 这里就是循环的判断 ----
        if not msg.tool_calls:
            if verbose:
                print(f"[第 {round_no} 轮] 模型不要工具了，给出答案\n")
            return msg.content

        # 模型要调工具：一个一个执行，把结果塞回对话
        for call in msg.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)
            result = dispatch(name, args)

            if verbose:
                print(f"[第 {round_no} 轮] 模型要调工具: {name}({args})")
                print(f"           工具返回 {len(result) if isinstance(result, list) else 1} 条\n")

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": json.dumps(result, ensure_ascii=False),
            })

    return "超过最大轮数还没得到答案。"


if __name__ == "__main__":
    import sys

    q = " ".join(sys.argv[1:]) or "上个月模型调用成本超了多少？是谁负责去查明细？"
    print(f"问题：{q}\n" + "-" * 50)
    print(run(q))
