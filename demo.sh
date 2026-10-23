#!/bin/bash
# 面试演示用：一条命令跑完四个场景
# 用法:  bash demo.sh
#        bash demo.sh "你自己的问题"

cd "$(dirname "$0")"

if [ -z "$DEEPSEEK_API_KEY" ]; then
  echo "没读到 DEEPSEEK_API_KEY，先运行:  source ~/.zshrc"
  exit 1
fi

if [ -n "$1" ]; then
  python3 agent.py "$1"
  exit 0
fi

QUESTIONS=(
  "上个月模型调用成本超了多少？谁负责去拉明细？"
  "我们都开过哪些会？"
  "转写在中英混说的场景下问题有多严重？"
  "区块链那场会上决定了什么？"
)

for q in "${QUESTIONS[@]}"; do
  echo "════════════════════════════════════════════════════"
  python3 agent.py "$q"
  echo
done
