"""
边界控制器 (Boundary Controller)
检查文档是否包含禁止修改的内容
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class BoundaryRule:
    name: str
    pattern: str
    description: str
    severity: str = "warning"  # warning, error
    is_regex: bool = True


class BoundaryController:
    """
    边界控制器
    检查文档是否包含禁止修改的内容
    """
    
    def __init__(self):
        self.rules: List[BoundaryRule] = []
        self._init_default_rules()
        self.protected_regions: List[Tuple[int, int]] = []  # (start, end) indices
    
    def _init_default_rules(self):
        """
        初始化默认规则
        """
        # 法律文档保护规则
        self.rules.extend([
            BoundaryRule(
                name="legal_signature",
                pattern=r"(?:签字|签名|盖章|签章)\s*[：:]\s*[^\n]{0,20}",
                description="法律签字区域",
                severity="error"
            ),
            BoundaryRule(
                name="legal_date",
                pattern=r"(?:日期|Date)\s*[：:]\s*\d{4}[/-]\d{1,2}[/-]\d{1,2}",
                description="日期字段",
                severity="error"
            ),
            BoundaryRule(
                name="legal_party",
                pattern=r"(?:甲方|乙方|丙方|双方|当事人)\s*[：:]\s*[^\n]+",
                description="合同当事人信息",
                severity="error"
            ),
            BoundaryRule(
                name="legal_amount",
                pattern=r"(?:金额|金额大写|Amount)\s*[：:]\s*[^\n]+",
                description="金额信息",
                severity="error"
            ),
            BoundaryRule(
                name="legal_article",
                pattern=r"第[一二三四五六七八九十百]+条\s*[^\n]{0,50}",
                description="法律条款标题",
                severity="warning"
            ),
        ])
        
        # 通用保护规则
        self.rules.extend([
            BoundaryRule(
                name="copyright",
                pattern=r"(?:©|Copyright)\s*\d{4}\s*[^\n]+",
                description="版权声明",
                severity="warning"
            ),
            BoundaryRule(
                name="important_note",
                pattern=r"(?:注意|WARNING|IMPORTANT|NOTE)\s*[：:]",
                description="重要提示",
                severity="warning",
                is_regex=True
            ),
        ])
    
    def add_rule(self, rule: BoundaryRule):
        """
        添加自定义规则
        """
        self.rules.append(rule)
        logger.info(f"添加边界规则: {rule.name}")
    
    def add_protected_region(self, start: int, end: int):
        """
        添加受保护的区域
        """
        self.protected_regions.append((start, end))
        logger.info(f"添加受保护区域: [{start}, {end}]")
    
    def check_permissions(self, text: str) -> Tuple[bool, List[Dict]]:
        """
        检查文档是否允许修改
        
        Returns:
            (allowed, violations) - 是否允许修改，违规列表
        """
        violations = []
        
        # 1. 检查规则匹配
        for rule in self.rules:
            try:
                if rule.is_regex:
                    matches = list(re.finditer(rule.pattern, text, re.IGNORECASE))
                else:
                    matches = []
                    idx = 0
                    while True:
                        idx = text.find(rule.pattern, idx)
                        if idx == -1:
                            break
                        matches.append(type('', (), {'start': lambda: idx, 'end': lambda: idx + len(rule.pattern)})())
                        idx += len(rule.pattern)
                
                for match in matches:
                    violations.append({
                        'rule': rule.name,
                        'description': rule.description,
                        'severity': rule.severity,
                        'start': match.start(),
                        'end': match.end(),
                        'matched_text': text[match.start():match.end()]
                    })
            except Exception as e:
                logger.error(f"规则检查失败 {rule.name}: {e}")
        
        # 2. 检查受保护区域
        # (这里简化处理，实际需要结合文本位置)
        
        # 判断是否允许
        has_error = any(v['severity'] == 'error' for v in violations)
        allowed = not has_error
        
        logger.info(f"边界检查完成: allowed={allowed}, violations={len(violations)}")
        
        return allowed, violations
    
    def get_modifiable_regions(self, text: str) -> List[Tuple[int, int]]:
        """
        获取可修改的区域
        """
        allowed, violations = self.check_permissions(text)
        
        if allowed and not violations:
            return [(0, len(text))]
        
        # 构建可修改区域（排除违规区域）
        modifiable = []
        last_end = 0
        
        # 按起始位置排序违规区域
        sorted_violations = sorted(violations, key=lambda x: x['start'])
        
        for v in sorted_violations:
            if v['start'] > last_end:
                modifiable.append((last_end, v['start']))
            last_end = max(last_end, v['end'])
        
        if last_end < len(text):
            modifiable.append((last_end, len(text)))
        
        return modifiable
    
    def validate_change(self, original_text: str, modified_text: str) -> Tuple[bool, List[str]]:
        """
        验证修改是否合法
        """
        issues = []
        
        # 检查受保护内容是否被修改
        allowed_original, violations_original = self.check_permissions(original_text)
        allowed_modified, violations_modified = self.check_permissions(modified_text)
        
        # 检查是否删除了重要内容
        for v_orig in violations_original:
            found = False
            for v_mod in violations_modified:
                if v_orig['matched_text'] in modified_text:
                    found = True
                    break
            
            if not found and v_orig['severity'] == 'error':
                issues.append(f"检测到受保护内容被删除: {v_orig['description']}")
        
        return len(issues) == 0, issues
