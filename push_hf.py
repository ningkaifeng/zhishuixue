# -*- coding: utf-8 -*-
'''把 hf_dataset/ 推到 Hugging Face Dataset（需要环境变量 HF_TOKEN）'''
import os, sys

token = os.environ.get('HF_TOKEN', '').strip()
if not token:
    print('[skip] HF_TOKEN 未配置，跳过推送 Hugging Face')
    sys.exit(0)

try:
    from huggingface_hub import HfApi
except ImportError:
    print('[skip] huggingface_hub 未安装')
    sys.exit(0)

REPO = 'zhishuixue/dst-decision-disclosure'

api = HfApi(token=token)
try:
    api.upload_folder(
        folder_path='hf_dataset',
        repo_id=REPO,
        repo_type='dataset',
        allow_patterns=['README.md', '*.jsonl', '*.md'],
        commit_message='Auto-sync dataset from zhishuixue.com build',
    )
    print('[ok] 已推送至 https://huggingface.co/datasets/' + REPO)
except Exception as e:
    # 推送失败不应让整个 build 失败
    print('[warn] 推送 Hugging Face 失败：%s' % e)
