"""

Ultracut provides some out of box usage functions including:

- apart: apart a video into background audio, srt, foreground audio, and segmented audio;


"""

from ultracutpro.tools.apart_video import ApartVideo


import argparse
import os
import sys


def main():
    # 主命令行解析器
    parser = argparse.ArgumentParser(
        prog="ultracut", description="Ultracut Pro 视频处理工具"
    )
    subparsers = parser.add_subparsers(title="可用命令", dest="command", required=True)

    # apart 子命令解析器
    apart_parser = subparsers.add_parser(
        "apart", help="分离视频：提取背景音乐、人声、字幕并分割音频"
    )
    apart_parser.add_argument("video_file", help="要处理的视频文件路径")
    apart_parser.add_argument(
        "--output_dir", "-o", default=None, help="输出文件目录 (默认: 当前目录)"
    )
    apart_parser.add_argument(
        "--keep_intermediate", "-k", action="store_true", help="保留中间处理文件"
    )

    args = parser.parse_args()

    # 处理apart命令
    if args.command == "apart":
        if not os.path.exists(args.video_file):
            sys.exit(f"错误：视频文件 '{args.video_file}' 不存在")

        if args.output_dir and not os.path.exists(args.output_dir):
            try:
                os.makedirs(args.output_dir)
            except OSError:
                sys.exit(f"错误：无法创建输出目录 '{args.output_dir}'")

        try:
            processor = ApartVideo(
                video_file=args.video_file,
                output_dir=args.output_dir,
                keep_intermediate=args.keep_intermediate,
            )
            processor.apart()
            print("✅ 视频分离完成！输出文件在:", os.path.abspath(processor.output_dir))
        except Exception as e:
            import traceback

            print(f"full trace: {traceback.format_exc()}")
            sys.exit(f"分离过程中出错: {str(e)}")


if __name__ == "__main__":
    main()
