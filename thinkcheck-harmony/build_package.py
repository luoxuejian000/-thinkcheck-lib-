#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
import sys

print("=" * 60)
print("ThinkCheck 3.0 包构建脚本")
print("=" * 60)

# 清理旧的构建文件
print("\n[1/3] 清理旧的构建文件...")
dirs_to_clean = ['dist', 'build', '*.egg-info']
for dir_pattern in dirs_to_clean:
    try:
        if os.path.exists(dir_pattern):
            if os.path.isdir(dir_pattern):
                import shutil
                shutil.rmtree(dir_pattern)
                print(f"  - 删除 {dir_pattern}")
    except Exception as e:
        print(f"  - 跳过 {dir_pattern}: {e}")

# 构建源分发包
print("\n[2/3] 构建源分发包 (sdist)...")
try:
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel', 'build'],
        capture_output=True,
        text=True
    )
    print("  - 依赖更新完成")
except Exception as e:
    print(f"  - 警告: {e}")

print("\n[3/3] 执行构建...")
try:
    result = subprocess.run(
        [sys.executable, '-m', 'build', '--sdist', '--wheel'],
        capture_output=True,
        text=True
    )
    print(f"  - 返回码: {result.returncode}")
    if result.stdout:
        print(f"\n标准输出:\n{result.stdout}")
    if result.stderr:
        print(f"\n标准错误:\n{result.stderr}")
    
    # 检查是否成功
    if os.path.exists('dist'):
        files = os.listdir('dist')
        if files:
            print(f"\n✅ 构建成功！生成的文件:")
            for f in files:
                print(f"   - {f}")
                size = os.path.getsize(os.path.join('dist', f))
                print(f"     大小: {size} 字节")
        else:
            print(f"\n❌ dist 目录存在但没有文件")
    else:
        print(f"\n❌ dist 目录未创建")
        
except Exception as e:
    print(f"\n❌ 构建失败: {e}")

print("\n" + "=" * 60)
