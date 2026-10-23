"""Agent 可以调用的工具。

每个工具就是一个普通的 Python 函数。
模型看到的是下面 TOOL_SCHEMAS 里的「说明书」，
决定要调哪个之后，由 dispatch() 真正执行。
"""

from data import NOTES


# ---------- 工具 1：列出所有会议 ----------

def list_meetings():
    """列出所有会议的日期和标题，不含正文。"""
    return [{"date": n["date"], "title": n["title"]} for n in NOTES]


# ---------- 工具 2：按关键词搜索会议纪要 ----------

def search_notes(keyword):
    """找出正文里包含 keyword 的会议，返回日期、标题和正文。

    找不到时返回空列表 []。
    """
    results = []
    for n in NOTES:
        if keyword in n["content"]:
            results.append(n)
    return results


# ---------- 模型看到的「说明书」 ----------

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "list_meetings",
            "description": "列出所有会议的日期和标题。当用户问有哪些会议、"
                           "或者需要先知道有什么会可查的时候用。",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_notes",
            "description": "在所有会议纪要的正文里搜索一个关键词，"
                           "返回包含该关键词的会议内容。",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "要搜索的关键词，例如 预算、准确率、导出",
                    }
                },
                "required": ["keyword"],
            },
        },
    },
]


# ---------- 名字 → 函数 ----------

REGISTRY = {
    "list_meetings": list_meetings,
    "search_notes": search_notes,
}


def dispatch(name, args):
    """按模型给的名字和参数，真正执行对应的函数。"""
    if name not in REGISTRY:
        return {"error": f"没有叫 {name} 的工具"}
    return REGISTRY[name](**args)
