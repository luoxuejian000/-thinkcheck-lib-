#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import shutil

print("=" * 60)
print("ThinkCheck 3.0 简单构建脚本")
print("=" * 60)

# 清理旧的构建文件
print("\n[1/2] 清理旧的构建文件...")
for dirname in ['dist', 'build', 'thinkcheck_harmony.egg-info']:
    try:
        if os.path.exists(dirname):
            if os.path.isdir(dirname):
                shutil.rmtree(dirname)
                print(f"  - 删除 {dirname}")
    except Exception as e:
        print(f"  - 跳过 {dirname}: {e}")

# 执行构建
print("\n[2/2] 执行构建...")
try:
    from setuptools import setup
    import sys
    
    # 构建 sdist
    print("  - 构建源分发包 (sdist)...")
    sys.argv = ['setup.py', 'sdist']
    from setuptools import setup
    import setup as our_setup  # 导入我们的 setup.py
    import importlib.util
    spec = importlib.util.spec_from_file_location("setup_module", "setup.py")
    setup_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(setup_module)
    
    # 构建 wheel
    print("  - 构建 wheel 分发包...")
    sys.argv = ['setup.py', 'bdist_wheel']
    spec.loader.exec_module(setup_module)
    
except Exception as e:
    print(f"  - 使用备用方法...")
    try:
        # 直接运行 setup.py
        import subprocess
        subprocess.run([sys.executable, 'setup.py', 'sdist'], check=True)
        subprocess.run([sys.executable, 'setup.py', 'bdist_wheel'], check=True)
    except Exception as e2:
        print(f"  ❌ 构建失败: {e2}")
        sys.exit(1)

# 检查结果
if os.path.exists('dist'):
    files = os.listdir('dist')
    if files:
        print(f"\n✅ 构建成功！")
        print(f"\n生成的文件:")
        for f in files:
            filepath = os.path.join('dist', f)
            size = os.path.getsize(filepath)
            print(f"   - {f} ({size:,} 字节)")
    else:
        print(f"\n❌ dist 目录存在但没有文件")
else:
    print(f"\n❌ dist 目录未创建")

print("\n" + "=" * 60)
