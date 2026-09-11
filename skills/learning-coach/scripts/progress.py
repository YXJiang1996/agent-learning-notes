#!/usr/bin/env python3
"""校验学习状态与引用；可选生成进度总览。仅依赖 Python 标准库。"""
import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

DIMENSIONS = ('概念理解', '源码追踪', '设计判断', '独立实现', '效果验证')
STATUSES = {'未评估', '学习中', '待验证', '已验证'}
ASSISTANCE = {'独立完成', '提示下完成', '共同完成', 'Agent生成', '自述'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def local_file(root, value):
    require(isinstance(value, str) and bool(value), '文件引用必须是非空相对路径')
    path = Path(value)
    require(not path.is_absolute() and '..' not in path.parts, f'引用必须在学习仓库内：{value}')
    resolved = (root / path).resolve()
    require(resolved.is_relative_to(root) and resolved.is_file(), f'文件不存在或超出学习仓库：{value}')
    return resolved


def date(value):
    require(isinstance(value, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', value), '日期必须为 YYYY-MM-DD')
    return dt.date.fromisoformat(value)


def validate(root, data):
    require(isinstance(data, dict) and data.get('schema_version') == 1, '不支持的进度格式版本')
    topics = data.get('topics')
    require(isinstance(topics, list), 'topics 必须是列表')
    ids = set()
    for topic in topics:
        require(isinstance(topic, dict), '主题必须是对象')
        ident = topic.get('id')
        require(isinstance(ident, str) and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', ident), '主题 ID 格式错误')
        require(ident not in ids, f'重复主题 ID：{ident}')
        ids.add(ident)
        require(isinstance(topic.get('title'), str) and topic['title'].strip(), f'{ident} 缺少标题')
        local_file(root, topic.get('path'))
        date(topic.get('updated_on'))
        if topic.get('review_on') is not None:
            date(topic['review_on'])
        require('review_on' in topic, f'{ident} 缺少 review_on；无安排请填 null')
        require(isinstance(topic.get('next_action'), str), f'{ident} 缺少下一步')
        require(isinstance(topic.get('weak_points'), list) and all(isinstance(x, str) for x in topic['weak_points']), f'{ident} 薄弱点必须是文本列表')
        deps = topic.get('prerequisites')
        require(isinstance(deps, list) and all(isinstance(x, str) for x in deps), f'{ident} 前置 ID 必须是文本列表')
        require(len(deps) == len(set(deps)), f'{ident} 前置 ID 重复')
        dimensions = topic.get('dimensions')
        require(isinstance(dimensions, dict) and set(dimensions) == set(DIMENSIONS), f'{ident} 必须包含五个掌握维度')
        for dimension, entry in dimensions.items():
            require(isinstance(entry, dict), f'{ident}/{dimension} 格式错误')
            status = entry.get('status')
            require(isinstance(status, str) and status in STATUSES, f'{ident}/{dimension} 状态无效')
            evidence = entry.get('evidence')
            require(isinstance(evidence, list), f'{ident}/{dimension} 缺少证据列表')
            levels = []
            for item in evidence:
                require(isinstance(item, dict), '证据必须是对象')
                local_file(root, item.get('path'))
                require(isinstance(item.get('summary'), str) and item['summary'].strip(), '证据缺少摘要')
                level = item.get('assistance')
                require(isinstance(level, str) and level in ASSISTANCE, '证据辅助程度无效')
                levels.append(level)
            if status == '已验证':
                require(any(x not in {'自述', 'Agent生成'} for x in levels), f'{ident}/{dimension} 已验证但缺少有效表现证据')
                if dimension == '独立实现':
                    require('独立完成' in levels, f'{ident} 独立实现缺少独立完成证据')
    graph = {topic['id']: topic['prerequisites'] for topic in topics}
    for ident, deps in graph.items():
        require(all(dep in ids for dep in deps), f'{ident} 引用了不存在的前置主题')
    # 迭代检测依赖环，避免深依赖触发递归限制。
    pending = {key: set(value) for key, value in graph.items()}
    while pending:
        ready = {key for key, value in pending.items() if not value}
        require(bool(ready), '前置知识存在循环依赖')
        pending = {key: value - ready for key, value in pending.items() if key not in ready}
    return topics


def cell(text):
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '&#124;').replace('\n', ' ')


def dashboard(topics):
    today = dt.date.today()
    lines = ['# 学习进度', '', f'生成日期：{today}。本文件由 progress/mastery.json 生成，请更新原始记录。', '',
             '各维度的已验证状态来自人工评估；结构校验不证明证据真实性。复核到期不会自动取消已验证状态。', '',
             '| 主题 | ' + ' | '.join(DIMENSIONS) + ' | 复核 | 下一步 |',
             '| --- | ' + ' | '.join(['---'] * 7) + ' |']
    for topic in topics:
        review = topic['review_on']
        review_label = '未安排' if review is None else ('需要复核：' if date(review) <= today else '') + review
        values = [topic['title']] + [topic['dimensions'][d]['status'] for d in DIMENSIONS] + [review_label, topic['next_action']]
        lines.append('| ' + ' | '.join(cell(x) for x in values) + ' |')
    if not topics:
        lines.extend(['', '尚未记录学习主题。'])
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path, help='学习仓库根目录')
    parser.add_argument('--write-dashboard', action='store_true', help='通过校验后写入进度总览')
    args = parser.parse_args()
    try:
        root = args.root.resolve()
        marker = json.loads(local_file(root, 'learning-hub.json').read_text(encoding='utf-8'))
        require(isinstance(marker, dict) and marker.get('schema_version') == 1, '缺少有效学习仓库标记')
        data = json.loads(local_file(root, 'progress/mastery.json').read_text(encoding='utf-8'))
        topics = validate(root, data)
        if args.write_dashboard:
            dest = root / 'progress/dashboard.md'
            require(not dest.is_symlink(), '总览不能是符号链接')
            require(dest.resolve().is_relative_to(root), '总览路径超出学习仓库')
            temp = dest.with_name('dashboard.md.tmp')
            # 排他创建：不会覆盖已有临时文件或跟随符号链接。
            with temp.open('x', encoding='utf-8') as handle:
                handle.write(dashboard(topics))
            temp.replace(dest)
        print(f'校验通过：{len(topics)} 个主题。' + ('已更新进度总览。' if args.write_dashboard else '未修改文件。'))
        return 0
    except (ValueError, OSError, TypeError) as error:
        print(f'校验失败：{error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
