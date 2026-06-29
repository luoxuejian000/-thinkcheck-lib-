"""
ThinkCheck Agent - 命令行入口
"""

import asyncio
import argparse
import sys
import yaml
import json
from pathlib import Path
from loguru import logger

from config import settings
from thinkcheck_agent.core.orchestration import Orchestrator, TaskContext
from thinkcheck_agent.core.evaluator import DocumentEvaluator
from thinkcheck_agent.core.actuator import HarmonyActuator
from thinkcheck_agent.tools.file_handler import FileHandler


def setup_logging():
    """配置日志"""
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 移除默认处理器
    logger.remove()
    
    # 控制台输出
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # 文件输出（按天轮转，保留7天）
    logger.add(
        log_file,
        level=settings.log_level,
        rotation="00:00",
        retention="7 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"
    )


def load_config(config_path: str = None):
    """加载配置文件"""
    config = {}
    
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            logger.info(f"已加载配置: {config_path}")
        except Exception as e:
            logger.warning(f"加载配置失败: {e}")
    
    return config


async def process_file(
    orchestrator: Orchestrator,
    file_handler: FileHandler,
    file_path: str,
    auto_fix: bool = False
):
    """处理单个文件"""
    logger.info(f"处理文件: {file_path}")
    
    # 读取文件
    content = file_handler.read_file(file_path)
    if not content:
        logger.error(f"无法读取文件: {file_path}")
        return None
    
    # 创建上下文
    context = TaskContext(
        file_path=file_path,
        original_content=content,
        workflow_type="legal_review",
        config={}
    )
    
    # 执行协调
    result = await orchestrator.orchestrate(context, auto_fix=auto_fix)
    
    # 保存修复结果
    if result.get('status') == 'success' and result.get('fixed_content'):
        fixed_path = file_handler.write_fixed_file(file_path, result['fixed_content'])
        logger.info(f"修复结果已保存: {fixed_path}")
        result['fixed_file_path'] = fixed_path
    
    return result


async def main():
    parser = argparse.ArgumentParser(description="ThinkCheck Agent for Enterprise")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("--file", help="处理单个文件")
    parser.add_argument("--dir", help="批量处理目录")
    parser.add_argument("--pattern", default="*.md", help="文件匹配模式")
    parser.add_argument("--workflow", default="legal_review", help="工作流类型")
    parser.add_argument("--no-fix", action="store_true", help="只评估不修复")
    parser.add_argument("--output", help="输出结果文件 (JSON)")
    parser.add_argument("--mode", default="full", choices=["simple", "full"], help="运行模式 (simple: 禁用 OCHR)")
    args = parser.parse_args()
    
    # 设置日志
    setup_logging()
    
    # 加载配置
    config = load_config(args.config)
    
    # 初始化组件
    logger.info("初始化 ThinkCheck Agent...")
    
    evaluator = DocumentEvaluator(config)
    actuator = HarmonyActuator(config)
    orchestrator = Orchestrator(
        evaluator,
        actuator,
        config,
        enable_ochr=(args.mode == "full")
    )
    file_handler = FileHandler()
    
    all_results = []
    
    try:
        if args.file:
            # 处理单个文件
            result = await process_file(
                orchestrator,
                file_handler,
                args.file,
                auto_fix=not args.no_fix
            )
            if result:
                all_results.append(result)
        
        elif args.dir:
            # 批量处理目录
            dir_path = Path(args.dir)
            if not dir_path.exists():
                logger.error(f"目录不存在: {args.dir}")
                return
            
            files = list(dir_path.glob(args.pattern))
            logger.info(f"找到 {len(files)} 个文件")
            
            for file_path in files:
                result = await process_file(
                    orchestrator,
                    file_handler,
                    str(file_path),
                    auto_fix=not args.no_fix
                )
                if result:
                    all_results.append(result)
        
        else:
            parser.print_help()
            return
        
        # 输出结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2)
            logger.info(f"结果已保存: {args.output}")
        else:
            # 控制台输出摘要
            print("\n" + "="*80)
            print("处理结果摘要")
            print("="*80)
            
            for r in all_results:
                print(f"\n文件: {r.get('request_id', 'N/A')}")
                print(f"状态: {r.get('status', 'N/A')}")
                
                if r.get('initial_scores'):
                    s = r['initial_scores']
                    print(f"初始分数: U={s['U']:.3f}, D={s['D']:.3f}, A={s['A']:.3f}, H={s['H']:.3f}")
                
                if r.get('final_scores'):
                    s = r['final_scores']
                    print(f"最终分数: U={s['U']:.3f}, D={s['D']:.3f}, A={s['A']:.3f}, H={s['H']:.3f}")
                    print(f"改进: {r.get('improvement', 0):+.3f}")
                
                if r.get('error'):
                    print(f"错误: {r['error']}")
            
            print("\n" + "="*80)
            
            # 会话摘要
            summary = orchestrator.get_session_summary()
            if summary:
                print("\n会话摘要:")
                print(f"  总评估数: {summary.get('total_evaluations', 0)}")
                print(f"  总修复数: {summary.get('total_repairs', 0)}")
                print(f"  总改进: {summary.get('total_improvement', 0):.3f}")
        
    except FileNotFoundError as e:
        logger.error(f"文件未找到: {e}")
    except KeyboardInterrupt:
        logger.warning("用户中断")
    except Exception as e:
        logger.exception(f"系统运行异常: {e}")


if __name__ == "__main__":
    asyncio.run(main())
