"""
Trace 模块 — 多维 U/D/A/H 轨迹追踪 V3 Pure

提供:
- U/D/A/H 四维全息轨迹追踪
- 矛盾驱动采样: 热点区域密集 + 其他区域稀疏
- 分段独立请求: 每次 2000 字符，防止超时
- 指数退避重试: 30s → 60s → 120s，最多 3 次
- 零预设零判定: 纯数据记录，不输出二元标签

导出:
- main: 主函数入口
- coarse_scan: 粗扫识别矛盾集中区域
- generate_sample_points: 生成采样点
- collect_multi_dim_data: 多维数据采集
- detect_flip_point: 自适应翻转点检测
- write_csv/write_json/write_report: 输出函数
"""

from .trajectory_v3_pure import (
    main,
    coarse_scan,
    generate_sample_points,
    collect_multi_dim_data,
    detect_flip_point,
    write_csv,
    write_json,
    write_report,
    evaluate_segment,
    validate_api_health,
    compute_h_driven_by,
    calculate_change_score,
)

__all__ = [
    "main",
    "coarse_scan",
    "generate_sample_points",
    "collect_multi_dim_data",
    "detect_flip_point",
    "write_csv",
    "write_json",
    "write_report",
    "evaluate_segment",
    "validate_api_health",
    "compute_h_driven_by",
    "calculate_change_score",
]
