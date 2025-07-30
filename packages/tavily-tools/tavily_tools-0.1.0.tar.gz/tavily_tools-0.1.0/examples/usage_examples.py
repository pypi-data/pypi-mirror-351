"""
Tavily Tools 使用示例集合

演示如何使用各种功能：
- 基础搜索和格式化
- 质量分析
- 批量处理
- 数据转换和导出
"""

import sys
from pathlib import Path

# 添加src目录到Python路径，以便导入tavily_tools
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from tavily_tools import SearchClient, TavilyFormatter, get_config, quick_format


def example_basic_usage():
    """示例1: 基础使用方法"""
    print("🔥 示例1: 基础使用方法")
    print("=" * 50)

    try:
        # 创建搜索客户端
        client = SearchClient()

        # 执行搜索
        response = client.search("Python机器学习库")

        # 创建格式化器
        formatter = TavilyFormatter(response)

        # 打印摘要
        formatter.print_summary()

        # 打印前3个结果
        print("\n📋 前3个搜索结果:")
        results = response.get("results", [])[:3]
        for i, result in enumerate(results, 1):
            print(f"\n[{i}] {result.get('title', '无标题')}")
            print(f"    评分: {result.get('score', 0):.3f}")
            print(f"    链接: {result.get('url', 'N/A')}")

    except Exception as e:
        print(f"❌ 示例1执行失败: {e}")


def example_advanced_formatting():
    """示例2: 高级格式化功能"""
    print("\n\n🚀 示例2: 高级格式化功能")
    print("=" * 50)

    try:
        client = SearchClient()
        response = client.search("Claude AI助手功能")

        # 完整格式化输出
        formatter = TavilyFormatter(response)

        print("📊 搜索结果完整分析:")
        formatter.print_full(max_content_length=100)

        # 转换为结构化数据
        structured = formatter.to_dict()
        print(f"\n✅ 结构化数据包含 {len(structured)} 个主要字段")

    except Exception as e:
        print(f"❌ 示例2执行失败: {e}")


def example_quality_analysis():
    """示例3: 搜索质量分析"""
    print("\n\n📊 示例3: 搜索质量分析")
    print("=" * 50)

    try:
        client = SearchClient()
        response = client.search("量子计算最新突破")

        formatter = TavilyFormatter(response)

        # 详细质量分析
        quality = formatter.analyze_quality()

        print("📈 详细质量分析:")
        print(f"   🔢 结果总数: {quality['结果总数']}")
        print(f"   ⭐ 平均评分: {quality['平均评分']:.4f}")
        print(f"   🎯 响应时间: {quality['响应时间']}秒")

        # 评分分布
        print(f"\n📊 评分分布:")
        for level, count in quality["评分分布"].items():
            print(f"   {level}: {count}条")

        # 评分分析
        if quality["平均评分"] > 0.7:
            print("✅ 搜索质量优秀")
        elif quality["平均评分"] > 0.4:
            print("⚠️  搜索质量中等")
        else:
            print("❌ 搜索质量偏低")

    except Exception as e:
        print(f"❌ 示例3执行失败: {e}")


def example_file_operations():
    """示例4: 文件操作和导出"""
    print("\n\n🔄 示例4: 文件操作和导出")
    print("=" * 50)

    try:
        client = SearchClient()
        response = client.search("人工智能伦理")

        formatter = TavilyFormatter(response)

        # 保存为JSON
        json_file = formatter.save_json(filename="ai_ethics_search.json")
        print(f"💾 JSON文件已保存: {json_file}")

        # 生成HTML报告
        html_file = formatter.save_html(filename="ai_ethics_report.html", title="AI伦理搜索报告")
        print(f"📄 HTML报告已生成: {html_file}")

        print("✅ 所有文件操作完成")

    except Exception as e:
        print(f"❌ 示例4执行失败: {e}")


def example_quick_format():
    """示例5: 快速格式化"""
    print("\n\n⚡ 示例5: 快速格式化")
    print("=" * 50)

    try:
        client = SearchClient()
        response = client.search("区块链技术应用")

        # 一键格式化，同时保存JSON和HTML
        formatter = quick_format(
            response, save_json=True, save_html=True, print_output=False  # 不重复打印
        )

        # 只显示摘要
        formatter.print_summary()

        print("✅ 快速格式化完成！已自动保存所有格式")

    except Exception as e:
        print(f"❌ 示例5执行失败: {e}")


def example_batch_processing():
    """示例6: 批量处理"""
    print("\n\n🔄 示例6: 批量处理")
    print("=" * 50)

    try:
        # 定义多个搜索主题
        search_topics = ["自然语言处理发展", "计算机视觉新技术", "强化学习应用"]

        print(f"🔍 准备批量搜索 {len(search_topics)} 个主题")

        # 使用SearchClient进行批量搜索
        client = SearchClient()
        results_summary = []

        for i, topic in enumerate(search_topics, 1):
            print(f"\n🔍 搜索 {i}/{len(search_topics)}: {topic}")

            try:
                # 执行搜索
                formatter = client.search_and_format(
                    query=topic, save_json=True, save_html=False, print_output=False
                )

                quality = formatter.analyze_quality()

                # 记录摘要
                summary = {
                    "主题": topic,
                    "结果数": quality["结果总数"],
                    "平均评分": quality["平均评分"],
                }
                results_summary.append(summary)

                print(
                    f"   ✅ 完成 | 结果: {quality['结果总数']}条 | 评分: {quality['平均评分']:.3f}"
                )

            except Exception as e:
                print(f"   ❌ 失败: {e}")

        # 显示批量处理总结
        print(f"\n📋 批量处理总结:")
        print("-" * 60)
        for summary in results_summary:
            print(f"   {summary['主题']}: {summary['结果数']}条结果，评分{summary['平均评分']:.3f}")

        if results_summary:
            avg_score = sum(s["平均评分"] for s in results_summary) / len(results_summary)
            total_results = sum(s["结果数"] for s in results_summary)
            print(f"\n📊 总体统计:")
            print(f"   处理主题: {len(results_summary)}")
            print(f"   总结果数: {total_results}")
            print(f"   平均评分: {avg_score:.3f}")

        print(f"\n🎉 批量处理完成！")

    except Exception as e:
        print(f"❌ 示例6执行失败: {e}")


def example_search_client_features():
    """示例7: SearchClient高级功能"""
    print("\n\n🎮 示例7: SearchClient高级功能")
    print("=" * 50)

    try:
        client = SearchClient()

        # 执行几次搜索以建立历史
        topics = ["Python编程", "机器学习", "数据科学"]

        for topic in topics:
            print(f"🔍 搜索: {topic}")
            client.search(topic)

        # 显示搜索历史
        history = client.get_search_history()
        print(f"\n📚 搜索历史（共{len(history)}条）:")
        for i, h in enumerate(history, 1):
            print(f"   {i}. {h['query']} - {h['results_count']}条结果")

        # 导出搜索历史
        history_file = client.export_history("search_history_demo.json")
        print(f"\n📁 搜索历史已导出: {history_file}")

        # 清空历史
        client.clear_history()
        print("🗑️ 搜索历史已清空")

    except Exception as e:
        print(f"❌ 示例7执行失败: {e}")


def run_all_examples():
    """运行所有示例"""
    print("🌟 Tavily Tools 完整示例演示")
    print("=" * 60)

    try:
        # 显示配置信息
        print("📋 当前配置:")
        config = get_config()
        config.show_config()

        # 运行所有示例
        example_basic_usage()
        example_advanced_formatting()
        example_quality_analysis()
        example_file_operations()
        example_quick_format()
        example_batch_processing()
        example_search_client_features()

        print(f"\n🎊 所有示例运行完成！")
        print("💡 提示：您可以查看生成的JSON和HTML文件")
        print("📁 所有输出文件保存在 results/ 目录中")

    except Exception as e:
        print(f"❌ 示例运行出错: {e}")
        import traceback

        traceback.print_exc()


def main():
    """主函数"""
    print("🎮 请选择要运行的示例:")
    print("1. 基础使用方法")
    print("2. 高级格式化功能")
    print("3. 搜索质量分析")
    print("4. 文件操作和导出")
    print("5. 快速格式化")
    print("6. 批量处理")
    print("7. SearchClient高级功能")
    print("8. 运行所有示例")

    choice = input("\n请输入选项 (1-8): ").strip()

    examples = {
        "1": example_basic_usage,
        "2": example_advanced_formatting,
        "3": example_quality_analysis,
        "4": example_file_operations,
        "5": example_quick_format,
        "6": example_batch_processing,
        "7": example_search_client_features,
        "8": run_all_examples,
    }

    if choice in examples:
        examples[choice]()
    else:
        print("❌ 无效选项")


if __name__ == "__main__":
    main()
