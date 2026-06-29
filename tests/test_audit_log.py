import pytest
from audit_log import AuditLog, OperationType


class TestAuditLog:
    def test_log_contradiction_flag(self):
        log = AuditLog("test")
        eid = log.log_contradiction_flag("c123", 0.74, "测试")
        assert len(log.entries) == 1
        entry = log.entries[0]
        assert entry.operation_type == OperationType.FLAG_CONTRADICTION
        assert entry.motivation == "测试"

    def test_rollback(self):
        log = AuditLog("test")
        eid = log.log_contradiction_flag("c123", 0.74, "测试")
        assert log.entries[0].status == "active"
        assert log.rollback(eid)
        assert log.entries[0].status == "rolled_back"
        assert log.entries[0].rolled_back_at is not None

    def test_export(self):
        log = AuditLog("test")
        log.log_contradiction_flag("c123", 0.74, "测试")
        data = log.export_to_dict()
        assert data["session_id"] == "test"
        assert data["total_entries"] == 1

    def test_get_entries_by_type(self):
        log = AuditLog("test")
        log.log_contradiction_flag("c1", 0.7, "测试1")
        log.log_flip_point_warning(10, 0.3, 0.5, 0.4, "测试2")
        entries = log.get_entries_by_type(OperationType.FLAG_CONTRADICTION)
        assert len(entries) == 1

    def test_get_recent(self):
        log = AuditLog("test")
        for i in range(60):
            log.log_contradiction_flag(f"c{i}", 0.7, f"测试{i}")
        recent = log.get_recent(50)
        assert len(recent) == 50

    def test_alternatives_field(self):
        """公理三：审计条目必须包含 alternatives 字段"""
        log = AuditLog("test")
        eid = log.log_contradiction_flag("c123", 0.74, "测试")
        entry = log.entries[0]
        assert len(entry.alternatives) > 0
        assert isinstance(entry.alternatives, list)

    def test_rollback_path_field(self):
        """公理三：审计条目必须包含 rollback_path 字段"""
        log = AuditLog("test")
        eid = log.log_contradiction_flag("c123", 0.74, "测试")
        entry = log.entries[0]
        assert entry.rollback_path != ""

    def test_motivation_field(self):
        """公理三：审计条目必须包含 motivation 字段"""
        log = AuditLog("test")
        eid = log.log_contradiction_flag("c123", 0.74, "测试动机")
        entry = log.entries[0]
        assert entry.motivation == "测试动机"

    def test_content_field(self):
        """公理三：审计条目必须包含 content 字段"""
        log = AuditLog("test")
        eid = log.log_contradiction_flag("c123", 0.74, "测试")
        entry = log.entries[0]
        assert "contradiction_id" in entry.content
        assert entry.content["a_value"] == 0.74