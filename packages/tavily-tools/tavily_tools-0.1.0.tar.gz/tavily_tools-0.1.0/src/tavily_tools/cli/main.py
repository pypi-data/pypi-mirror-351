"""
Tavily Tools 命令行接口

提供完整的命令行功能：
- 交互式搜索
- 批量搜索
- 配置管理
- 搜索历史
"""

import argparse
import sys
from typing import List, Optional

from ..config.settings import get_config, validate_environment
from ..core.formatter import TavilyFormatter
from ..core.search import SearchClient, batch_search, interactive_search
from ..utils.helpers import format_timestamp


def create_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器

    Returns:
        配置好的参数解析器
    """
    parser = argparse.ArgumentParser(
        prog="tavily-tools",
        description="Tavily搜索结果格式化工具 - 提供智能搜索和多格式输出",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  tavily-tools                           # 交互式搜索
  tavily-tools -q "Python编程"           # 快速搜索
  tavily-tools -b "AI" "机器学习" "深度学习"  # 批量搜索
  tavily-tools --config                  # 显示配置信息
  tavily-tools --validate-env            # 验证环境配置
        """,
    )

    # 基本操作选项
    parser.add_argument("-q", "--query", type=str, help="执行单次搜索查询")

    parser.add_argument("-b", "--batch", nargs="+", metavar="QUERY", help="批量搜索多个查询")

    parser.add_argument(
        "-i", "--interactive", action="store_true", help="启动交互式搜索模式（默认）"
    )

    # 输出选项
    parser.add_argument("--save-json", action="store_true", help="保存结果为JSON文件")

    parser.add_argument("--save-html", action="store_true", help="生成HTML报告")

    parser.add_argument("--no-print", action="store_true", help="不打印搜索结果到控制台")

    parser.add_argument("--output-dir", type=str, help="指定输出目录")

    # 配置和信息选项
    parser.add_argument("--config", action="store_true", help="显示当前配置信息")

    parser.add_argument("--validate-env", action="store_true", help="验证环境配置")

    parser.add_argument("--version", action="version", version="Tavily Tools 0.1.0")

    # 搜索参数
    parser.add_argument("--max-results", type=int, default=10, help="最大搜索结果数量（默认：10）")

    parser.add_argument("--timeout", type=int, default=30, help="搜索超时时间，秒（默认：30）")

    # 调试选项
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出模式")

    parser.add_argument("--quiet", action="store_true", help="安静模式，最小化输出")

    return parser


def handle_single_search(args: argparse.Namespace) -> None:
    """
    处理单次搜索

    Args:
        args: 命令行参数
    """
    try:
        client = SearchClient()

        if args.verbose:
            print(f"🔍 执行搜索: {args.query}")

        # 执行搜索
        formatter = client.search_and_format(
            query=args.query,
            save_json=args.save_json,
            save_html=args.save_html,
            print_output=not args.no_print,
        )

        # 显示质量分析
        if not args.quiet:
            quality = formatter.analyze_quality()
            print(f"\n📊 搜索质量: {quality['平均评分']:.3f} | 结果数: {quality['结果总数']}")

    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        sys.exit(1)


def handle_batch_search(args: argparse.Namespace) -> None:
    """
    处理批量搜索

    Args:
        args: 命令行参数
    """
    try:
        if args.verbose:
            print(f"🔄 开始批量搜索，共 {len(args.batch)} 个查询")

        formatters = batch_search(
            topics=args.batch,
            save_json=args.save_json,
            save_html=args.save_html,
            print_progress=not args.quiet,
        )

        if not args.quiet and formatters:
            # 显示总结
            total_results = sum(f.analyze_quality()["结果总数"] for f in formatters)
            avg_score = sum(f.analyze_quality()["平均评分"] for f in formatters) / len(formatters)

            print(f"\n📋 批量搜索完成:")
            print(f"   处理查询: {len(formatters)}")
            print(f"   总结果数: {total_results}")
            print(f"   平均评分: {avg_score:.3f}")

    except Exception as e:
        print(f"❌ 批量搜索失败: {e}")
        sys.exit(1)


def handle_config_display(args: argparse.Namespace) -> None:
    """
    处理配置显示

    Args:
        args: 命令行参数
    """
    try:
        config = get_config()
        config.show_config(show_sensitive=args.verbose)

        if args.verbose:
            config_dict = config.to_dict()
            print(f"\n📝 详细配置:")
            for key, value in config_dict.items():
                print(f"   {key}: {value}")

    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        sys.exit(1)


def handle_environment_validation(args: argparse.Namespace) -> None:
    """
    处理环境验证

    Args:
        args: 命令行参数
    """
    print("🔍 验证环境配置...")

    if validate_environment():
        print("✅ 环境配置正确")

        if args.verbose:
            try:
                from ..config.settings import get_tavily_client

                client = get_tavily_client()
                print("✅ Tavily客户端初始化成功")
            except Exception as e:
                print(f"⚠️  客户端初始化警告: {e}")
    else:
        print("❌ 环境配置有问题")
        print("请检查.env文件和API密钥配置")
        sys.exit(1)


def run_cli(args: Optional[List[str]] = None) -> None:
    """
    运行命令行接口

    Args:
        args: 命令行参数列表，None时使用sys.argv
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # 处理不同的操作模式
    try:
        if parsed_args.config:
            handle_config_display(parsed_args)
        elif parsed_args.validate_env:
            handle_environment_validation(parsed_args)
        elif parsed_args.query:
            handle_single_search(parsed_args)
        elif parsed_args.batch:
            handle_batch_search(parsed_args)
        else:
            # 默认进入交互式模式
            if not parsed_args.quiet:
                print("🌟 欢迎使用 Tavily Tools!")
                print("=" * 50)
            interactive_search()

    except KeyboardInterrupt:
        print(f"\n\n🛑 程序被用户中断")
        sys.exit(0)
    except Exception as e:
        if parsed_args.verbose:
            import traceback

            traceback.print_exc()
        else:
            print(f"❌ 程序运行出错: {e}")
        sys.exit(1)


def main() -> None:
    """
    主入口函数 - 兼容原有调用方式
    """
    print("🌟 欢迎使用 Tavily 搜索结果格式化工具!")
    print("=" * 60)

    try:
        # 显示菜单
        print("请选择操作模式:")
        print("1. 交互式搜索 (推荐)")
        print("2. 批量搜索示例")
        print("3. 显示配置信息")
        print("4. 验证环境配置")
        print("5. 退出")

        choice = input("\n请输入选项 (1-5): ").strip()

        if choice == "1":
            interactive_search()
        elif choice == "2":
            from ..core.search import batch_search_example

            batch_search_example()
        elif choice == "3":
            handle_config_display(argparse.Namespace(verbose=False))
        elif choice == "4":
            handle_environment_validation(argparse.Namespace(verbose=True))
        elif choice == "5":
            print("👋 感谢使用，再见!")
        else:
            print("❌ 无效选项，请重新运行程序")

    except Exception as e:
        print(f"❌ 程序运行出错: {e}")


if __name__ == "__main__":
    run_cli()
