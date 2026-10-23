"""会议纪要问答 Agent。

一轮循环：把问题和工具 schema 发给模型 -> 模型返回 tool_calls ->
本地执行 -> 结果以 role="tool" 写回 messages -> 再次请求模型。
模型不再请求工具时返回最终回答。
"""

import json
import os

from openai import OpenAI

from tools import TOOL_SCHEMAS, dispatch

MODEL = "deepseek-chat"
MAX_ROUNDS = 5          # 上限，避免模型反复请求工具导致不收敛

SYSTEM_PROMPT = """你是一个会议纪要助手。

规则：
1. 回答之前必须先用工具查会议纪要，不要凭记忆编。
2. 工具查不到就直说查不到，不要猜。
3. 回答里要带上信息来自哪一场会（日期 + 标题）。
4. 回答简短，中文。"""


def make_client():
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        raise SystemExit("未读取到 DEEPSEEK_API_KEY，请先设置环境变量")
    return OpenAI(api_key=key, base_url="https://api.deepseek.com")


def run(question, verbose=True):
    """执行一次完整的 Agent 循环，返回最终回答。"""
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

        if not msg.tool_calls:
            if verbose:
                print(f"[第 {round_no} 轮] 无工具请求，返回最终回答\n")
            return msg.content

        # 模型请求了工具：逐个执行并把结果写回 messages
        for call in msg.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)
            result = dispatch(name, args)

            if verbose:
                print(f"[第 {round_no} 轮] 工具请求: {name}({args})")
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
