"""
Tavily搜索客户端封装

提供高级搜索功能：
- 单次搜索
- 交互式搜索
- 批量搜索
- 搜索历史管理
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..config.settings import get_config, get_tavily_client
from ..utils.helpers import format_timestamp
from .formatter import TavilyFormatter, quick_format


class SearchClient:
    """
    Tavily搜索客户端封装类

    提供统一的搜索接口和结果处理
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化搜索客户端

        Args:
            api_key: API密钥，如不提供则从配置读取
        """
        if api_key:
            from tavily import TavilyClient

            self.client = TavilyClient(api_key)
        else:
            self.client = get_tavily_client()

        self.config = get_config()
        self.search_history: List[Dict[str, Any]] = []

    def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        执行搜索

        Args:
            query: 搜索查询
            **kwargs: Tavily搜索的其他参数

        Returns:
            搜索响应结果
        """
        try:
            print(f"🔍 正在搜索: {query}")
            response = self.client.search(query=query, **kwargs)

            # 记录搜索历史
            self.search_history.append(
                {
                    "query": query,
                    "timestamp": datetime.now().isoformat(),
                    "results_count": len(response.get("results", [])),
                    "response_time": response.get("response_time", "N/A"),
                }
            )

            print(f"✅ 搜索完成，共获得 {len(response.get('results', []))} 条结果")
            return response

        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            raise

    def search_and_format(
        self,
        query: str,
        save_json: bool = False,
        save_html: bool = False,
        print_output: bool = True,
        **kwargs,
    ) -> TavilyFormatter:
        """
        搜索并格式化结果

        Args:
            query: 搜索查询
            save_json: 是否保存JSON
            save_html: 是否生成HTML报告
            print_output: 是否打印输出
            **kwargs: 其他搜索参数

        Returns:
            格式化器实例
        """
        response = self.search(query, **kwargs)
        return quick_format(response, save_json, save_html, print_output)

    def get_search_history(self) -> List[Dict[str, Any]]:
        """
        获取搜索历史

        Returns:
            搜索历史列表
        """
        return self.search_history.copy()

    def clear_history(self) -> None:
        """清空搜索历史"""
        self.search_history.clear()
        print("🗑️ 搜索历史已清空")

    def export_history(self, filename: Optional[str] = None) -> Optional[str]:
        """
        导出搜索历史

        Args:
            filename: 导出文件名

        Returns:
            导出文件路径
        """
        if not self.search_history:
            print("❌ 没有搜索历史可导出")
            return None

        if not filename:
            filename = f"search_history_{format_timestamp()}.json"

        try:
            filepath = self.config.results_save_path + "/" + filename
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.search_history, f, ensure_ascii=False, indent=2)

            print(f"📁 搜索历史已导出: {filepath}")
            return filepath

        except Exception as e:
            print(f"❌ 导出失败: {e}")
            return None


def interactive_search():
    """
    交互式搜索功能
    提供用户友好的搜索体验和结果展示
    """
    try:
        # 获取配置和客户端
        config = get_config()
        client = SearchClient()

        # 显示配置信息
        config.show_config()

        # 获取搜索查询
        search_query = input(
            f"\n🔍 请输入搜索关键词 (默认: {config.default_search_query}): "
        ).strip()
        if not search_query:
            search_query = config.default_search_query

        print(f"🚀 正在搜索...")

        # 执行搜索和格式化
        formatter = client.search_and_format(
            query=search_query, save_json=False, save_html=False, print_output=True
        )

        # 分析质量
        quality = formatter.analyze_quality()
        print(f"\n📈 搜索质量分析:")
        print(f"   结果总数: {quality['结果总数']}")
        print(f"   平均评分: {quality['平均评分']:.3f}")
        print(f"   高质量结果: {quality['评分分布']['高质量(>0.7)']}")
        print(f"   中等质量结果: {quality['评分分布']['中等质量(0.4-0.7)']}")
        print(f"   低质量结果: {quality['评分分布']['低质量(<0.4)']}")
        print(f"   响应时间: {quality['响应时间']}")

        # 询问是否保存结果
        save_json = input(f"\n💾 是否保存搜索结果到JSON文件？(y/n): ").lower().strip()
        if save_json in ["y", "yes", "是"]:
            filename = formatter.save_json()
            print(f"\n💾 搜索结果已保存到: {filename}")
            print("✅ 结果已成功保存!")

        # 询问是否显示原始响应
        show_raw = input(f"\n📋 是否显示原始JSON响应？(y/n): ").lower().strip()
        if show_raw in ["y", "yes", "是"]:
            print(f"\n{'='*80}")
            print("📋 原始JSON响应:")
            print("=" * 80)
            print(json.dumps(formatter.response, ensure_ascii=False, indent=2))

        # 询问是否生成HTML报告
        save_html = input(f"\n📄 是否生成HTML报告？(y/n): ").lower().strip()
        if save_html in ["y", "yes", "是"]:
            html_filename = formatter.save_html(title=f"Tavily搜索报告 - {search_query}")
            print(f"\n📄 HTML报告已生成: {html_filename}")
            print("✅ 报告已成功保存!")

    except KeyboardInterrupt:
        print(f"\n\n🛑 搜索已被用户中断")
    except Exception as e:
        print(f"\n❌ 搜索过程中发生错误: {e}")
        print("请检查网络连接和API密钥配置")


def batch_search(
    topics: Union[List[str], str],
    save_json: bool = True,
    save_html: bool = False,
    print_progress: bool = True,
) -> List[TavilyFormatter]:
    """
    批量搜索功能

    Args:
        topics: 搜索主题列表或单个主题
        save_json: 是否保存JSON文件
        save_html: 是否生成HTML报告
        print_progress: 是否显示进度

    Returns:
        格式化器列表
    """
    # 处理输入参数
    if isinstance(topics, str):
        topics = [topics]

    if not topics:
        print("❌ 没有提供搜索主题")
        return []

    try:
        client = SearchClient()
        formatters = []

        if print_progress:
            print(f"🔄 开始批量搜索，共 {len(topics)} 个主题...")

        for i, topic in enumerate(topics, 1):
            if print_progress:
                print(f"\n📍 正在搜索第{i}个主题: {topic}")

            try:
                # 执行搜索和格式化
                formatter = client.search_and_format(
                    query=topic,
                    save_json=save_json,
                    save_html=save_html,
                    print_output=False,  # 批量处理时不打印详细输出
                )

                formatters.append(formatter)

                # 显示质量摘要
                if print_progress:
                    quality = formatter.analyze_quality()
                    print(
                        f"   ✅ 完成 | 结果数: {quality['结果总数']} | 平均评分: {quality['平均评分']:.3f}"
                    )

            except Exception as e:
                if print_progress:
                    print(f"   ❌ 搜索失败: {e}")
                continue

        if print_progress:
            print(f"\n🎉 批量搜索完成！共处理 {len(formatters)} 个主题")

            # 显示搜索历史统计
            history = client.get_search_history()
            if history:
                total_results = sum(h["results_count"] for h in history)
                print(f"📊 总计获得 {total_results} 条搜索结果")

        return formatters

    except Exception as e:
        print(f"❌ 批量搜索失败: {e}")
        return []


def batch_search_example():
    """
    批量搜索示例
    展示如何进行多个主题的批量搜索
    """
    # 定义搜索主题
    topics = ["人工智能最新发展", "量子计算突破", "自动驾驶技术"]

    print("🔄 开始批量搜索示例...")

    try:
        # 执行批量搜索
        formatters = batch_search(
            topics=topics, save_json=True, save_html=False, print_progress=True
        )

        # 生成总结报告
        if formatters:
            print(f"\n📋 批量搜索总结:")
            print("-" * 60)

            for i, formatter in enumerate(formatters):
                quality = formatter.analyze_quality()
                topic = topics[i] if i < len(topics) else f"主题{i+1}"
                print(f"   {topic}: {quality['结果总数']}条结果，评分{quality['平均评分']:.3f}")

    except Exception as e:
        print(f"❌ 批量搜索示例失败: {e}")


# 向后兼容的函数名
def main():
    """主函数 - 向后兼容"""
    print("🌟 欢迎使用 Tavily 搜索结果格式化工具!")
    print("=" * 60)

    try:
        # 显示菜单
        print("请选择操作模式:")
        print("1. 交互式搜索 (推荐)")
        print("2. 批量搜索示例")
        print("3. 退出")

        choice = input("\n请输入选项 (1-3): ").strip()

        if choice == "1":
            interactive_search()
        elif choice == "2":
            batch_search_example()
        elif choice == "3":
            print("👋 感谢使用，再见!")
        else:
            print("❌ 无效选项，请重新运行程序")

    except Exception as e:
        print(f"❌ 程序运行出错: {e}")


if __name__ == "__main__":
    main()
