"""
法律文档审阅工作流
"""
from typing import Dict, Any
from datetime import datetime
from pathlib import Path
from loguru import logger


class LegalDocumentReviewWorkflow:
    def __init__(self, orchestrator, file_handler):
        self.orchestrator = orchestrator
        self.file_handler = file_handler

    async def execute(self, content: str, file_path: str, auto_fix: bool = True) -> Dict[str, Any]:
        logger.info(f"开始法律文档审阅: {file_path}")
        start_time = datetime.now()
        context = self.orchestrator.TaskContext(
            file_path=file_path,
            original_content=content,
            workflow_type="legal_review",
            intermediate_results={'workflow_start': start_time.isoformat()},
            config=self.orchestrator.config
        )
        try:
            result = await self.orchestrator.orchestrate(context) if auto_fix else {"status": "evaluation_only"}
            result.update({
                'processing_time_seconds': (datetime.now() - start_time).total_seconds(),
                'timestamp': datetime.now().isoformat()
            })
            return result
        except Exception as e:
            logger.error(f"审阅失败: {e}")
            return {"status": "error", "error": str(e)}