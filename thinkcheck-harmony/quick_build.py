#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import shutil
import subprocess

print("=" * 60)
print("ThinkCheck 3.0 快速构建")
print("=" * 60)

# 清理
for dirname in ['dist', 'build', 'thinkcheck_harmony.egg-info']:
    if os.path.exists(dirname):
        shutil.rmtree(dirname)
        print(f"删除 {dirname}")

# 构建
print("\n开始构建...")

try:
    # sdist
    print("  1. 构建源分发包...")
    result = subprocess.run(
        [sys.executable, 'setup.py', 'sdist'],
        capture_output=True,
        text=True
    )
    print(f"     返回码: {result.returncode}")
    if result.stdout:
        print(f"     输出: {result.stdout[:100]}...")
    if result.stderr:
        print(f"     错误: {result.stderr[:100]}...")
    
    # bdist_wheel
    print("  2. 构建 wheel 包...")
    result = subprocess.run(
        [sys.executable, 'setup.py', 'bdist_wheel'],
        capture_output=True,
        text=True
    )
    print(f"     返回码: {result.returncode}")
    if result.stdout:
        print(f"     输出: {result.stdout[:100]}...")
    if result.stderr:
        print(f"     错误: {result.stderr[:100]}...")
    
except Exception as e:
    print(f"错误: {e}")

# 检查
if os.path.exists('dist'):
    files = os.listdir('dist')
    if files:
        print(f"\n✅ 成功！构建了 {len(files)} 个文件:")
        for f in files:
            filepath = os.path.join('dist', f)
            size = os.path.getsize(filepath)
            print(f"   - {f} ({size} bytes)")
    else:
        print("\n❌ dist 目录存在但无文件")
else:
    print("\n❌ 未生成 dist 目录")

print("\n" + "=" * 60)
