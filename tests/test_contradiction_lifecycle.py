import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'thinkcheck-harmony'))

import pytest
from thinkcheck_harmony.contradiction_lifecycle import (
    ContradictionLifecycleManager, Contradiction, ContradictionStage
)


class TestContradictionLifecycle:
    def test_create(self):
        manager = ContradictionLifecycleManager()
        cid = manager.create("A", "B", 0.8)
        assert manager.contradictions[cid].stage == ContradictionStage.DORMANT

    def test_detect(self):
        manager = ContradictionLifecycleManager()
        cid = manager.create("A", "B", 0.8)
        manager.detect(cid)
        assert manager.contradictions[cid].stage == ContradictionStage.EMERGENT

    def test_present_to_user(self):
        manager = ContradictionLifecycleManager()
        cid = manager.create("A", "B", 0.8)
        manager.detect(cid)
        manager.present_to_user(cid)
        assert manager.contradictions[cid].stage == ContradictionStage.NOTICED

    def test_user_views(self):
        manager = ContradictionLifecycleManager()
        cid = manager.create("A", "B", 0.8)
        manager.detect(cid)
        manager.present_to_user(cid)
        manager.user_views(cid)
        assert manager.contradictions[cid].stage == ContradictionStage.PROCESSING

    def test_user_resolve(self):
        manager = ContradictionLifecycleManager()
        cid = manager.create("A", "B", 0.8)
        manager.detect(cid)
        manager.present_to_user(cid)
        manager.user_views(cid)
        manager.user_resolves(cid, "维持原有立场")
        c = manager.contradictions[cid]
        assert c.stage in (ContradictionStage.RESOLVED, ContradictionStage.TRANSFORMED)

    def test_user_resolve_transformed(self):
        manager = ContradictionLifecycleManager()
        cid = manager.create("A", "B", 0.8)
        manager.detect(cid)
        manager.present_to_user(cid)
        manager.user_views(cid)
        manager.user_resolves(cid, "转化为新理解")
        c = manager.contradictions[cid]
        assert c.stage == ContradictionStage.TRANSFORMED

    def test_system_cannot_resolve(self):
        """系统不能自主将矛盾转换到 RESOLVED 状态"""
        manager = ContradictionLifecycleManager()
        cid = manager.create("A", "B", 0.8)
        # 系统没有 system_resolve 方法
        assert not hasattr(manager, 'system_resolve')
        # 系统唯一可自主执行的是 detect()
        manager.detect(cid)
        assert manager.contradictions[cid].stage == ContradictionStage.EMERGENT

    def test_get_active(self):
        manager = ContradictionLifecycleManager()
        cid1 = manager.create("A", "B", 0.8)
        cid2 = manager.create("C", "D", 0.6)
        manager.detect(cid1)
        manager.present_to_user(cid1)
        manager.user_views(cid1)
        manager.user_resolves(cid1, "已解决")
        # cid2 还是 DORMANT，所以是活跃的
        # cid1 是 RESOLVED，所以不是活跃的
        active = manager.get_active()
        assert len(active) == 1
        assert active[0].id == cid2

    def test_get_summary(self):
        manager = ContradictionLifecycleManager()
        manager.create("A", "B", 0.8)
        manager.create("C", "D", 0.6)
        summary = manager.get_summary()
        assert summary["dormant"] == 2

    def test_audit_trail(self):
        manager = ContradictionLifecycleManager()
        cid = manager.create("A", "B", 0.8)
        manager.detect(cid)
        trail = manager.get_audit_trail(cid)
        assert len(trail) == 1
        assert trail[0]["from_stage"] == "dormant"
        assert trail[0]["to_stage"] == "emergent"