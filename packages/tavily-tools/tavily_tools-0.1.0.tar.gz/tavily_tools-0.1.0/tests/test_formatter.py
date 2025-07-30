"""
TavilyFormatter 测试

测试格式化器的各种功能：
- 基础格式化
- 数据转换
- 文件输出
- 质量分析
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from tavily_tools.core.formatter import TavilyFormatter, quick_format


class TestTavilyFormatter(unittest.TestCase):
    """TavilyFormatter测试类"""

    def setUp(self):
        """测试前准备"""
        self.sample_response = {
            "query": "测试查询",
            "response_time": 1.23,
            "answer": "这是AI的回答",
            "results": [
                {
                    "title": "测试标题1",
                    "url": "https://example.com/1",
                    "content": "测试内容1",
                    "score": 0.85,
                },
                {
                    "title": "测试标题2",
                    "url": "https://example.com/2",
                    "content": "测试内容2",
                    "score": 0.65,
                },
            ],
            "follow_up_questions": ["相关问题1", "相关问题2"],
        }

        # 使用临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.formatter = TavilyFormatter(self.sample_response, self.temp_dir)

    def test_load_response(self):
        """测试加载响应数据"""
        formatter = TavilyFormatter()
        result = formatter.load_response(self.sample_response)

        self.assertEqual(result, formatter)  # 应该返回self
        self.assertEqual(formatter.response, self.sample_response)

    def test_to_dict(self):
        """测试转换为字典"""
        result = self.formatter.to_dict()

        self.assertIsInstance(result, dict)
        self.assertIn("搜索信息", result)
        self.assertIn("AI答案", result)
        self.assertIn("搜索结果", result)
        self.assertIn("跟进问题", result)

        # 检查搜索信息
        search_info = result["搜索信息"]
        self.assertEqual(search_info["查询"], "测试查询")
        self.assertEqual(search_info["响应时间"], 1.23)
        self.assertEqual(search_info["结果数量"], 2)

        # 检查搜索结果
        search_results = result["搜索结果"]
        self.assertEqual(len(search_results), 2)
        self.assertEqual(search_results[0]["标题"], "测试标题1")
        self.assertEqual(search_results[0]["评分"], 0.85)

    def test_analyze_quality(self):
        """测试质量分析"""
        quality = self.formatter.analyze_quality()

        self.assertIsInstance(quality, dict)
        self.assertEqual(quality["结果总数"], 2)
        self.assertAlmostEqual(quality["平均评分"], 0.75, places=2)
        self.assertEqual(quality["响应时间"], 1.23)

        # 检查评分分布
        distribution = quality["评分分布"]
        self.assertEqual(distribution["高质量(>0.7)"], 1)
        self.assertEqual(distribution["中等质量(0.4-0.7)"], 1)
        self.assertEqual(distribution["低质量(<0.4)"], 0)

    def test_save_json(self):
        """测试JSON保存"""
        filename = self.formatter.save_json("test_output.json")

        self.assertIsNotNone(filename)

        # 验证文件存在且内容正确
        json_path = Path(filename)
        self.assertTrue(json_path.exists())

        with open(json_path, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)

        self.assertIn("搜索信息", loaded_data)
        self.assertEqual(loaded_data["搜索信息"]["查询"], "测试查询")

    def test_save_html(self):
        """测试HTML保存"""
        filename = self.formatter.save_html("test_report.html", "测试报告")

        self.assertIsNotNone(filename)

        # 验证文件存在且包含HTML内容
        html_path = Path(filename)
        self.assertTrue(html_path.exists())

        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        self.assertIn("<!DOCTYPE html>", html_content)
        self.assertIn("测试报告", html_content)
        self.assertIn("测试查询", html_content)
        self.assertIn("测试标题1", html_content)

    def test_empty_response(self):
        """测试空响应处理"""
        formatter = TavilyFormatter()

        # 没有响应数据时的行为
        self.assertIsNone(formatter.to_dict())

        quality = formatter.analyze_quality()
        self.assertEqual(quality, {})

        # 保存操作应该失败但不抛出异常
        json_result = formatter.save_json()
        html_result = formatter.save_html()

        self.assertIsNone(json_result)
        self.assertIsNone(html_result)

    def test_quick_format(self):
        """测试快速格式化函数"""
        with patch("builtins.print"):  # 抑制打印输出
            formatter = quick_format(
                self.sample_response, save_json=False, save_html=False, print_output=False
            )

        self.assertIsInstance(formatter, TavilyFormatter)
        self.assertEqual(formatter.response, self.sample_response)

    @patch("builtins.print")
    def test_print_methods(self, mock_print):
        """测试打印方法"""
        # 测试打印摘要
        self.formatter.print_summary()
        mock_print.assert_called()

        # 测试打印结果
        mock_print.reset_mock()
        self.formatter.print_results()
        mock_print.assert_called()

        # 测试完整打印
        mock_print.reset_mock()
        self.formatter.print_full()
        mock_print.assert_called()


class TestFormatterEdgeCases(unittest.TestCase):
    """测试边缘情况"""

    def test_malformed_response(self):
        """测试畸形响应数据"""
        malformed_response = {
            "query": None,
            "results": [{"title": "", "score": "invalid"}, {}],  # 无效评分  # 空结果
        }

        formatter = TavilyFormatter(malformed_response)

        # 应该能处理而不崩溃
        quality = formatter.analyze_quality()
        self.assertIsInstance(quality, dict)

        structured = formatter.to_dict()
        self.assertIsInstance(structured, dict)

    def test_special_characters_in_content(self):
        """测试内容中的特殊字符"""
        response_with_special_chars = {
            "query": "测试<script>alert('xss')</script>",
            "results": [
                {
                    "title": "包含&amp;特殊&lt;字符&gt;的标题",
                    "content": "包含\"引号\"和'单引号'的内容",
                    "url": "https://example.com/test?param=value&other=123",
                    "score": 0.8,
                }
            ],
        }

        formatter = TavilyFormatter(response_with_special_chars)

        # 生成HTML时应该正确转义
        with tempfile.TemporaryDirectory() as temp_dir:
            formatter.save_path = temp_dir
            html_file = formatter.save_html()

            with open(html_file, "r", encoding="utf-8") as f:
                html_content = f.read()

            # 不应该包含未转义的脚本标签
            self.assertNotIn("<script>", html_content)
            self.assertIn("&lt;script&gt;", html_content)


if __name__ == "__main__":
    unittest.main()
