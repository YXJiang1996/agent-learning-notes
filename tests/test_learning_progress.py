"""使用临时学习仓库验证真实进度更新边界，不写入个人学习数据。"""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/learning-coach/scripts/progress.py'
DIMENSIONS = ('概念理解', '源码追踪', '设计判断', '独立实现', '效果验证')


class ProgressTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'learning-hub.json').write_text('{"schema_version":1,"language":"zh-CN"}')
        (self.root / 'progress').mkdir()
        (self.root / 'topic.md').write_text('# 测试主题')
        (self.root / 'evidence.md').write_text('模拟隔离测试证据；不属于用户学习记录。')
        self.topic = dict(id='memory', title='记忆机制', path='topic.md', prerequisites=[],
                          dimensions={d:dict(status='未评估', evidence=[]) for d in DIMENSIONS},
                          weak_points=[], next_action='继续研究', review_on='2000-01-01', updated_on='2026-09-11')

    def run_progress(self, topics, write=True):
        (self.root / 'progress/mastery.json').write_text(json.dumps(dict(schema_version=1, topics=topics)))
        args = [sys.executable, str(SCRIPT), '--root', str(self.root)]
        if write:
            args.append('--write-dashboard')
        return subprocess.run(args, text=True, capture_output=True)

    def test_empty_and_read_only(self):
        self.assertEqual(self.run_progress([], False).returncode, 0)
        self.assertFalse((self.root / 'progress/dashboard.md').exists())
        self.assertEqual(self.run_progress([]).returncode, 0)
        self.assertIn('尚未记录', (self.root / 'progress/dashboard.md').read_text())

    def test_verified_evidence_and_due_review(self):
        self.topic['dimensions']['独立实现'] = dict(status='已验证', evidence=[dict(path='evidence.md', summary='通过关键改动与解释检查', assistance='独立完成')])
        result = self.run_progress([self.topic])
        self.assertEqual(result.returncode, 0, result.stderr)
        view = (self.root / 'progress/dashboard.md').read_text()
        self.assertIn('已验证', view)
        self.assertIn('需要复核', view)

    def test_unverified_claim_does_not_overwrite_dashboard(self):
        output = self.root / 'progress/dashboard.md'
        output.write_text('原来的有效总览')
        self.topic['dimensions']['概念理解']['status'] = '已验证'
        self.assertNotEqual(self.run_progress([self.topic]).returncode, 0)
        self.assertEqual(output.read_text(), '原来的有效总览')

    def test_assistance_cannot_prove_independent_implementation(self):
        for level in ('Agent生成', '自述', '共同完成', '提示下完成'):
            with self.subTest(level=level):
                self.topic['dimensions']['独立实现'] = dict(status='已验证', evidence=[dict(path='evidence.md', summary='测试证据', assistance=level)])
                self.assertNotEqual(self.run_progress([self.topic]).returncode, 0)

    def test_missing_reference_and_outside_path(self):
        for path in ('missing.md', '../outside.md', str(self.root / 'topic.md')):
            with self.subTest(path=path):
                self.topic['path'] = path
                self.assertNotEqual(self.run_progress([self.topic]).returncode, 0)

    def test_dependency_errors(self):
        other = copy.deepcopy(self.topic)
        other['id'] = 'sandbox'
        for topics in ([self.topic, self.topic], [dict(self.topic, prerequisites=['missing'])],
                       [dict(self.topic, prerequisites=['sandbox']), dict(other, prerequisites=['memory'])]):
            self.assertNotEqual(self.run_progress(topics).returncode, 0)

    def test_valid_dependency_and_invalid_date(self):
        other = copy.deepcopy(self.topic)
        other.update(id='sandbox', prerequisites=['memory'])
        self.assertEqual(self.run_progress([self.topic, other]).returncode, 0)
        other['review_on'] = '2026-02-30'
        self.assertNotEqual(self.run_progress([self.topic, other]).returncode, 0)

    def test_output_symlink_refused(self):
        (self.root / 'progress/dashboard.md').symlink_to(self.root / 'evidence.md')
        self.assertNotEqual(self.run_progress([self.topic]).returncode, 0)
        self.assertIn('模拟隔离测试证据', (self.root / 'evidence.md').read_text())


if __name__ == '__main__':
    unittest.main()
