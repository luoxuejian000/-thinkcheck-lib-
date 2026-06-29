"""
OCHR - 和谐治理模块
用于文档治理的核心功能：关系映射、反思腔、边界控制、审计日志、L3元反思
"""

from .boundary import BoundaryController
from .reflection_cavity import ReflectionCavity, AuditEntry
from .relationship_mapper import RelationshipMapper

# 从根目录导入（如果存在）
try:
    from audit_log import AuditLog, OperationType
except ImportError:
    AuditLog = None
    OperationType = None

try:
    from l3_reflection import L3ReflectionEngine, GovernanceHealthReport, RulePerformance
except ImportError:
    L3ReflectionEngine = None
    GovernanceHealthReport = None
    RulePerformance = None

__version__ = "1.0.0"
__all__ = [
    "BoundaryController",
    "ReflectionCavity",
    "AuditEntry",
    "RelationshipMapper",
    "AuditLog",
    "OperationType",
    "L3ReflectionEngine",
    "GovernanceHealthReport",
    "RulePerformance",
]