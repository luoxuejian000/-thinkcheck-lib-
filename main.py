import asyncio
import argparse
import logging
import yaml
from thinkcheck_agent.core.orchestration import Orchestrator, TaskContext
from thinkcheck_agent.core.evaluator import DocumentEvaluator
from thinkcheck_agent.core.actuator import HarmonyActuator
from thinkcheck_agent.tools.file_handler import FileHandler


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def main():
    parser = argparse.ArgumentParser(description="ThinkCheck Agent for Enterprise")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("--file", help="处理单个文件")
    parser.add_argument("--dir", help="批量处理目录")
    parser.add_argument("--pattern", default="*.md", help="文件匹配模式")
    parser.add_argument("--workflow", default="legal_review", help="工作流类型")
    args = parser.parse_args()
    try:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        evaluator = DocumentEvaluator(config)
        actuator = HarmonyActuator(config)
        orchestrator = Orchestrator(evaluator, actuator, config)
        file_handler = FileHandler()
        if args.file:
            content = file_handler.read_file(args.file)
            if not content:
                logger.error("文件读取失败，退出。")
                return
            context = TaskContext(file_path=args.file, original_content=content, workflow_type=args.workflow, config=config)
            result = await orchestrator.orchestrate(context)
            if result.get('status') == 'success' and 'fixed_content' in result:
                file_handler.write_fixed_file(args.file, result['fixed_content'])
                logger.info(f"调谐成功！和谐度提升: {result.get('improvement', 0):.3f}")
            else:
                logger.info(f"状态: {result.get('status')}")
        elif args.dir:
            logger.warning("批量处理功能将在后续版本中完善。")
        else:
            parser.print_help()
    except FileNotFoundError:
        logger.error(f"配置文件未找到: {args.config}")
    except Exception as e:
        logger.exception(f"系统运行异常: {e}")


if __name__ == "__main__":
    asyncio.run(main())
