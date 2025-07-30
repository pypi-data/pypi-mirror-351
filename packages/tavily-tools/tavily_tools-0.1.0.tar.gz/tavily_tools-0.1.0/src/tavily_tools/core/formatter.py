"""
Tavily搜索结果格式化器

提供多种格式化输出选项，包括：
- 控制台美化输出
- JSON结构化保存
- HTML报告生成
- 搜索质量分析
"""

import html
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils.helpers import clean_filename, ensure_directory, format_timestamp


class TavilyFormatter:
    """
    Tavily搜索结果格式化器

    支持多种输出格式和质量分析功能
    """

    def __init__(self, response: Optional[Dict[str, Any]] = None, save_path: Optional[str] = None):
        """
        初始化格式化器

        Args:
            response: Tavily搜索响应数据
            save_path: 保存路径，默认使用配置中的路径
        """
        self.response = response
        self.save_path = save_path or self._get_default_save_path()

        # 确保保存目录存在
        ensure_directory(self.save_path)

    def _get_default_save_path(self) -> str:
        """获取默认保存路径"""
        try:
            from ..config.settings import get_config

            config = get_config()
            return config.results_save_path
        except ImportError:
            # 如果无法导入config，使用默认路径
            return "./results/"

    def load_response(self, response: Dict[str, Any]) -> "TavilyFormatter":
        """
        加载搜索响应数据

        Args:
            response: Tavily搜索响应

        Returns:
            self: 支持链式调用
        """
        self.response = response
        return self

    def print_summary(self) -> None:
        """打印搜索摘要信息"""
        if not self.response:
            print("❌ 没有搜索数据")
            return

        print("=" * 60)
        print(f"🔍 查询: {self.response.get('query', 'N/A')}")
        print(f"⏱️  用时: {self.response.get('response_time', 'N/A')}秒")
        print(f"📊 结果: {len(self.response.get('results', []))}条")
        print("=" * 60)

    def print_results(self, max_content_length: int = 150) -> None:
        """
        打印搜索结果

        Args:
            max_content_length: 内容摘要的最大长度
        """
        if not self.response:
            print("❌ 没有搜索数据")
            return

        results = self.response.get("results", [])

        for i, result in enumerate(results, 1):
            print(f"\n📄 [{i}] {result.get('title', '无标题')}")
            print(f"   🔗 {result.get('url', 'N/A')}")
            print(f"   ⭐ 评分: {result.get('score', 0):.3f}")

            content = result.get("content", "")
            if content:
                if len(content) > max_content_length:
                    content = content[:max_content_length] + "..."
                print(f"   📝 {content}")
            print("-" * 50)

    def print_full(self, max_content_length: int = 150) -> None:
        """
        打印完整的格式化结果

        Args:
            max_content_length: 内容摘要的最大长度
        """
        self.print_summary()

        # AI答案
        if self.response and self.response.get("answer"):
            print(f"\n💡 AI答案:")
            print(f"{self.response['answer']}")
            print("-" * 50)

        # 搜索结果
        self.print_results(max_content_length)

        # 跟进问题
        if self.response and self.response.get("follow_up_questions"):
            print(f"\n❓ 相关问题:")
            for i, question in enumerate(self.response["follow_up_questions"], 1):
                print(f"   {i}. {question}")

    def to_dict(self) -> Optional[Dict[str, Any]]:
        """
        转换为结构化字典

        Returns:
            格式化后的字典数据
        """
        if not self.response:
            return None

        formatted = {
            "搜索信息": {
                "查询": self.response.get("query"),
                "响应时间": self.response.get("response_time"),
                "结果数量": len(self.response.get("results", [])),
            },
            "AI答案": self.response.get("answer"),
            "搜索结果": [],
            "跟进问题": self.response.get("follow_up_questions", []),
        }

        for i, result in enumerate(self.response.get("results", []), 1):
            formatted["搜索结果"].append(
                {
                    "序号": i,
                    "标题": result.get("title"),
                    "链接": result.get("url"),
                    "评分": result.get("score"),
                    "内容摘要": result.get("content"),
                }
            )

        return formatted

    def save_json(self, filename: Optional[str] = None, formatted: bool = True) -> Optional[str]:
        """
        保存为JSON文件

        Args:
            filename: 文件名，默认自动生成
            formatted: 是否使用格式化数据

        Returns:
            保存的文件名
        """
        if not self.response:
            print("❌ 没有搜索数据")
            return None

        if not filename:
            query = self.response.get("query", "search")
            filename = f"tavily_{clean_filename(query)}_{format_timestamp()}.json"

        # 确保文件名不包含路径，然后拼接保存路径
        filename = Path(filename).name
        filepath = Path(self.save_path) / filename

        try:
            data = self.to_dict() if formatted else self.response
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"💾 已保存到: {filepath}")
            return str(filepath)

        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return None

    def save_html(
        self, filename: Optional[str] = None, title: Optional[str] = None
    ) -> Optional[str]:
        """
        生成HTML报告

        Args:
            filename: 文件名，默认自动生成
            title: 报告标题

        Returns:
            保存的文件名
        """
        if not self.response:
            print("❌ 没有搜索数据")
            return None

        if not filename:
            query = self.response.get("query", "search")
            filename = f"tavily_{clean_filename(query)}_{format_timestamp()}.html"

        if not title:
            title = f"Tavily搜索报告 - {self.response.get('query', '未知查询')}"

        filename = Path(filename).name
        filepath = Path(self.save_path) / filename

        try:
            html_content = self._generate_html_content(title)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)

            print(f"📄 已生成HTML报告: {filepath}")
            return str(filepath)

        except Exception as e:
            print(f"❌ HTML生成失败: {e}")
            return None

    def _generate_html_content(self, title: str) -> str:
        """
        生成HTML内容

        Args:
            title: 报告标题

        Returns:
            完整的HTML内容
        """
        if not self.response:
            return ""

        # 基础信息
        query = html.escape(str(self.response.get("query", "N/A")))
        response_time = self.response.get("response_time", "N/A")
        results_count = len(self.response.get("results", []))
        answer = html.escape(str(self.response.get("answer", "")))

        # 搜索结果HTML
        results_html = ""
        for i, result in enumerate(self.response.get("results", []), 1):
            title_text = html.escape(str(result.get("title", "无标题")))
            url = html.escape(str(result.get("url", "#")))
            score = result.get("score", 0)
            content = html.escape(str(result.get("content", "")))

            results_html += f"""
            <div class="result-item">
                <h3 class="result-title">
                    <span class="result-number">[{i}]</span>
                    <a href="{url}" target="_blank">{title_text}</a>
                </h3>
                <div class="result-meta">
                    <span class="result-score">评分: {score:.3f}</span>
                    <span class="result-url">{url}</span>
                </div>
                <div class="result-content">{content}</div>
            </div>
            """

        # 跟进问题HTML
        follow_up_html = ""
        if self.response.get("follow_up_questions"):
            follow_up_html = "<h2>💡 相关问题</h2><ul class='follow-up-questions'>"
            for question in self.response["follow_up_questions"]:
                question_text = html.escape(str(question))
                follow_up_html += f"<li>{question_text}</li>"
            follow_up_html += "</ul>"

        # 生成时间
        generation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2.5em;
        }}
        .meta-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .meta-item {{
            text-align: center;
        }}
        .meta-label {{
            font-weight: bold;
            color: #666;
            font-size: 0.9em;
        }}
        .meta-value {{
            font-size: 1.2em;
            color: #333;
            margin-top: 5px;
        }}
        .ai-answer {{
            background: #e8f5e8;
            border-left: 4px solid #28a745;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .ai-answer h2 {{
            color: #28a745;
            margin-top: 0;
        }}
        .results-section {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 20px 0;
        }}
        .result-item {{
            border-bottom: 1px solid #eee;
            padding: 20px 0;
        }}
        .result-item:last-child {{
            border-bottom: none;
        }}
        .result-title {{
            margin: 0 0 10px 0;
            color: #1a73e8;
        }}
        .result-title a {{
            color: inherit;
            text-decoration: none;
        }}
        .result-title a:hover {{
            text-decoration: underline;
        }}
        .result-number {{
            background: #1a73e8;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-right: 10px;
        }}
        .result-meta {{
            color: #666;
            font-size: 0.9em;
            margin: 5px 0;
        }}
        .result-score {{
            background: #f0f8ff;
            color: #1a73e8;
            padding: 2px 8px;
            border-radius: 4px;
            margin-right: 10px;
        }}
        .result-url {{
            color: #666;
            word-break: break-all;
        }}
        .result-content {{
            margin-top: 10px;
            line-height: 1.5;
            color: #444;
        }}
        .follow-up-questions {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .follow-up-questions h2 {{
            color: #856404;
            margin-top: 0;
        }}
        .follow-up-questions ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .follow-up-questions li {{
            margin: 8px 0;
            color: #856404;
        }}
        .footer {{
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin-top: 40px;
            padding: 20px;
            border-top: 1px solid #eee;
        }}
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            .header h1 {{
                font-size: 2em;
            }}
            .meta-info {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{html.escape(title)}</h1>
        <p>基于Tavily AI搜索引擎的智能搜索报告</p>
    </div>
    
    <div class="meta-info">
        <div class="meta-item">
            <div class="meta-label">🔍 搜索查询</div>
            <div class="meta-value">{query}</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">⏱️ 响应时间</div>
            <div class="meta-value">{response_time}秒</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">📊 结果数量</div>
            <div class="meta-value">{results_count}条</div>
        </div>
        <div class="meta-item">
            <div class="meta-label">📅 生成时间</div>
            <div class="meta-value">{generation_time}</div>
        </div>
    </div>
    
    {f'<div class="ai-answer"><h2>🤖 AI智能答案</h2><p>{answer}</p></div>' if answer else ''}
    
    <div class="results-section">
        <h2>🔍 搜索结果</h2>
        {results_html}
    </div>
    
    {follow_up_html}
    
    <div class="footer">
        <p>📄 报告生成时间: {generation_time}</p>
        <p>🔧 由 Tavily Tools 强力驱动</p>
    </div>
</body>
</html>
        """

    def analyze_quality(self) -> Dict[str, Any]:
        """
        分析搜索质量

        Returns:
            质量分析报告
        """
        if not self.response:
            return {}

        results = self.response.get("results", [])
        if not results:
            return {
                "结果总数": 0,
                "平均评分": 0,
                "评分分布": {"高质量(>0.7)": 0, "中等质量(0.4-0.7)": 0, "低质量(<0.4)": 0},
                "响应时间": self.response.get("response_time", "N/A"),
            }

        # 计算评分统计 - 确保评分为数值类型
        scores = []
        for result in results:
            score = result.get("score", 0)
            try:
                # 尝试转换为浮点数
                score = float(score) if score is not None else 0.0
                # 确保评分在合理范围内
                score = max(0.0, min(1.0, score))
            except (ValueError, TypeError):
                # 如果转换失败，使用默认值0
                score = 0.0
            scores.append(score)

        # 计算平均分
        avg_score = sum(scores) / len(scores) if scores else 0.0

        # 评分分布
        high_quality = sum(1 for score in scores if score > 0.7)
        medium_quality = sum(1 for score in scores if 0.4 <= score <= 0.7)
        low_quality = sum(1 for score in scores if score < 0.4)

        return {
            "结果总数": len(results),
            "平均评分": avg_score,
            "评分分布": {
                "高质量(>0.7)": high_quality,
                "中等质量(0.4-0.7)": medium_quality,
                "低质量(<0.4)": low_quality,
            },
            "响应时间": self.response.get("response_time", "N/A"),
        }


def quick_format(
    response: Dict[str, Any],
    save_json: bool = False,
    save_html: bool = False,
    print_output: bool = True,
) -> TavilyFormatter:
    """
    快速格式化函数

    Args:
        response: Tavily搜索响应
        save_json: 是否保存JSON文件
        save_html: 是否生成HTML报告
        print_output: 是否打印输出

    Returns:
        格式化器实例
    """
    formatter = TavilyFormatter(response)

    if print_output:
        formatter.print_full()

    if save_json:
        formatter.save_json()

    if save_html:
        formatter.save_html()

    return formatter
