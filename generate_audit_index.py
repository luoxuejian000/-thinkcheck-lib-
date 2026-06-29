"""
长文本审计索引表生成脚本
窗格大小：2000字符
"""

import os

file_path = "万象渊鉴·场域诊断测试集.txt"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

total_chars = len(content)
pane_size = 2000
num_panes = (total_chars + pane_size - 1) // pane_size

output_lines = []
output_lines.append("=" * 80)
output_lines.append("【长文本审计索引表】")
output_lines.append("=" * 80)
output_lines.append(f"文件路径: {file_path}")
output_lines.append(f"总字符数: {total_chars}")
output_lines.append(f"窗格大小: {pane_size} 字符")
output_lines.append(f"总窗格数: {num_panes}")
output_lines.append("=" * 80)
output_lines.append("")
output_lines.append(f"{'窗格编号':<10} {'起始位置':<12} {'终止位置':<12} {'内容主题':<50} {'时序关系':<15}")
output_lines.append("-" * 100)

panes = []
for i in range(num_panes):
    start = i * pane_size
    end = min((i + 1) * pane_size, total_chars)
    pane_content = content[start:end]
    
    summary = pane_content[:50].replace("\n", " ").replace("\r", " ")
    if len(summary) < 50:
        summary = summary.ljust(50)
    
    if i == 0:
        timeline = "起点"
    elif i == num_panes - 1:
        timeline = "终点"
    else:
        timeline = "连续推进"
    
    panes.append({
        "number": i + 1,
        "start": start,
        "end": end,
        "summary": summary,
        "timeline": timeline
    })
    
    output_lines.append(f"{i+1:<10} {start:<12} {end:<12} {summary:<50} {timeline:<15}")

output_lines.append("")
output_lines.append("=" * 80)
output_lines.append(f"索引表生成完成，共 {num_panes} 个窗格")
output_lines.append("=" * 80)

output_file = "长文本审计索引表.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print(f"索引表已保存到: {output_file}")