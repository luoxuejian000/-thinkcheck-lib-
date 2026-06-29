#!/usr/bin/env python3
"""
HTML可视化报告生成器 V3 Pure+ Pro
纯数据呈现，不含任何判定
"""

import json
import os
from datetime import datetime


def generate_html_report(json_file: str, output_file: str = None) -> str:
    """
    从JSON数据生成HTML可视化报告
    所有图表仅呈现数据，不包含任何判定或建议
    """
    if not os.path.exists(json_file):
        raise FileNotFoundError(f"JSON文件不存在: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if output_file is None:
        output_file = json_file.replace('.json', '_report.html')
    
    trajectory = data if isinstance(data, list) else data.get('trajectory', [])
    if not trajectory:
        raise ValueError("未找到轨迹数据")
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>场域诊断可视化报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f7f7f8; padding: 40px 20px; color: #1d1d1f; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #1a1a2e, #16213e); color: #fff; padding: 30px 40px; border-radius: 16px; margin-bottom: 30px; }}
        .header h1 {{ font-size: 28px; font-weight: 600; }}
        .header .sub {{ font-size: 14px; color: #a0a0b0; margin-top: 8px; }}
        .header .meta {{ display: flex; gap: 30px; margin-top: 16px; flex-wrap: wrap; }}
        .header .meta span {{ font-size: 13px; color: #c0c0d0; }}
        .card {{ background: #fff; border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }}
        .card h2 {{ font-size: 16px; font-weight: 600; color: #1d1d1f; margin-bottom: 16px; border-bottom: 1px solid #e5e5ea; padding-bottom: 8px; }}
        .chart-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        @media (max-width: 768px) {{ .chart-grid {{ grid-template-columns: 1fr; }} }}
        .chart-box {{ position: relative; height: 220px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; }}
        .stat-item {{ background: #f5f5f7; padding: 12px 16px; border-radius: 8px; text-align: center; }}
        .stat-item .val {{ font-size: 24px; font-weight: 600; color: #1d1d1f; }}
        .stat-item .lbl {{ font-size: 12px; color: #8e8e93; margin-top: 4px; }}
        .footnote {{ text-align: center; color: #8e8e93; font-size: 12px; margin-top: 20px; padding-top: 20px; border-top: 1px solid #e5e5ea; }}
        .footnote strong {{ color: #1d1d1f; }}
        .drift-section {{ margin-top: 20px; padding: 16px; background: #fafafa; border-radius: 8px; }}
        .drift-section h3 {{ font-size: 14px; color: #1d1d1f; margin-bottom: 12px; }}
        .drift-table {{ width: 100%; border-collapse: collapse; }}
        .drift-table th, .drift-table td {{ padding: 8px 12px; text-align: left; font-size: 13px; }}
        .drift-table th {{ background: #e5e5ea; color: #8e8e93; }}
        .drift-table td {{ border-bottom: 1px solid #e5e5ea; }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>📊 场域诊断可视化报告</h1>
        <div class="sub">纯数据呈现 · 不包含任何判定或建议</div>
        <div class="meta">
            <span>📄 数据点: {len(trajectory)}</span>
            <span>📅 生成: {datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
            <span>⚙️ 引擎: V3 Pure+ Pro</span>
        </div>
    </div>
    
    <div class="card">
        <h2>📈 四维轨迹 (U/D/A/H)</h2>
        <div class="chart-grid">
            <div class="chart-box"><canvas id="chartU"></canvas></div>
            <div class="chart-box"><canvas id="chartD"></canvas></div>
            <div class="chart-box"><canvas id="chartA"></canvas></div>
            <div class="chart-box"><canvas id="chartH"></canvas></div>
        </div>
    </div>
    
    <div class="card">
        <h2>📊 数据摘要</h2>
        <div class="stats-grid">
            <div class="stat-item"><div class="val" id="uRange">-</div><div class="lbl">U值范围</div></div>
            <div class="stat-item"><div class="val" id="dRange">-</div><div class="lbl">D值范围</div></div>
            <div class="stat-item"><div class="val" id="aRange">-</div><div class="lbl">A值范围</div></div>
            <div class="stat-item"><div class="val" id="hRange">-</div><div class="lbl">H值范围</div></div>
            <div class="stat-item"><div class="val" id="flipCount">0</div><div class="lbl">翻转点数量</div></div>
            <div class="stat-item"><div class="val" id="aNonZero">0%</div><div class="lbl">A值非零占比</div></div>
        </div>
    </div>
    
    <div class="card">
        <h2>📊 一阶差分轨迹 (ΔU/ΔD/ΔA)</h2>
        <div class="chart-grid">
            <div class="chart-box"><canvas id="chartDeltaU"></canvas></div>
            <div class="chart-box"><canvas id="chartDeltaD"></canvas></div>
            <div class="chart-box"><canvas id="chartDeltaA"></canvas></div>
            <div class="chart-box"><canvas id="chartCumulA"></canvas></div>
        </div>
    </div>
    
    <div class="footnote">
        本报告仅呈现诊断数据，不构成任何行动建议。<br>
        所有阈值和判定标准均应由观察者基于数据自行定义。<br>
        <strong>判断权在您手中</strong>
    </div>
</div>

<script>
const data = {json.dumps(trajectory, ensure_ascii=False)};
const steps = data.map(d => d.step || d.char_pos || 0);
const u = data.map(d => d.U || 0);
const d = data.map(d => d.D || 0);
const a = data.map(d => d.A || 0);
const h = data.map(d => d.H || 0);
const uDiff = data.map(d => d.U_diff || 0);
const dDiff = data.map(d => d.D_diff || 0);
const aDiff = data.map(d => d.A_diff || 0);
const cumulA = data.map(d => d.cumul_A || 0);

function createChart(id, label, values, color) {{
    const ctx = document.getElementById(id).getContext('2d');
    new Chart(ctx, {{
        type: 'line',
        data: {{
            labels: steps,
            datasets: [ {{
                label: label,
                data: values,
                borderColor: color,
                backgroundColor: color + '22',
                fill: true,
                tension: 0.3,
                pointRadius: 2,
                pointBackgroundColor: color,
                borderWidth: 2
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{ display: false }},
                tooltip: {{
                    callbacks: {{
                        label: function(ctx) {{
                            return ctx.dataset.label + ': ' + ctx.parsed.y.toFixed(3);
                        }}
                    }}
                }}
            }},
            scales: {{
                y: {{ min: 0, max: 1, ticks: {{ stepSize: 0.2 }} }},
                x: {{ display: false }}
            }}
        }}
    }});
}}

function createDiffChart(id, label, values, color) {{
    const ctx = document.getElementById(id).getContext('2d');
    new Chart(ctx, {{
        type: 'line',
        data: {{
            labels: steps,
            datasets: [ {{
                label: label,
                data: values,
                borderColor: color,
                backgroundColor: color + '22',
                fill: true,
                tension: 0.3,
                pointRadius: 2,
                borderWidth: 2
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{ display: false }},
                tooltip: {{
                    callbacks: {{
                        label: function(ctx) {{
                            return ctx.dataset.label + ': ' + ctx.parsed.y.toFixed(3);
                        }}
                    }}
                }}
            }},
            scales: {{
                x: {{ display: false }}
            }}
        }}
    }});
}}

// 创建四维轨迹图
createChart('chartU', 'U值', u, '#3b82f6');
createChart('chartD', 'D值', d, '#10b981');
createChart('chartA', 'A值', a, '#f59e0b');
createChart('chartH', 'H值', h, '#8b5cf6');

// 创建一阶差分图
createDiffChart('chartDeltaU', 'ΔU', uDiff, '#3b82f6');
createDiffChart('chartDeltaD', 'ΔD', dDiff, '#10b981');
createDiffChart('chartDeltaA', 'ΔA', aDiff, '#f59e0b');
createDiffChart('chartCumulA', 'ΣA累积', cumulA, '#ef4444');

// 计算数据摘要
const uMin = Math.min(...u).toFixed(3);
const uMax = Math.max(...u).toFixed(3);
const dMin = Math.min(...d).toFixed(3);
const dMax = Math.max(...d).toFixed(3);
const aMin = Math.min(...a).toFixed(3);
const aMax = Math.max(...a).toFixed(3);
const hMin = Math.min(...h).toFixed(3);
const hMax = Math.max(...h).toFixed(3);

const aNonZeroCount = a.filter(v => v > 0.001).length;
const aNonZeroPct = ((aNonZeroCount / a.length) * 100).toFixed(1);

// 更新统计卡片
document.getElementById('uRange').textContent = uMin + ' - ' + uMax;
document.getElementById('dRange').textContent = dMin + ' - ' + dMax;
document.getElementById('aRange').textContent = aMin + ' - ' + aMax;
document.getElementById('hRange').textContent = hMin + ' - ' + hMax;
document.getElementById('aNonZero').textContent = aNonZeroPct + '%';
</script>
</body>
</html>'''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return output_file


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='HTML可视化报告生成器 V3 Pure+ Pro',
        epilog='本系统仅生成数据可视化，不包含任何判定或建议。'
    )
    parser.add_argument('json_file', help='JSON数据文件路径')
    parser.add_argument('--output', '-o', help='输出HTML文件路径')
    
    args = parser.parse_args()
    
    try:
        output_path = generate_html_report(args.json_file, args.output)
        print(f"[OK] HTML报告已生成: {output_path}")
    except Exception as e:
        print(f"[FAIL] 生成失败: {e}")