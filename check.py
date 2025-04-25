import sys
from pathlib import Path


def check_files(directory):
    required_files = ["draft_content.json", "draft_meta_info.json"]
    directory_path = Path(directory)
    missing_files = []

    for file in required_files:
        if not (directory_path / file).exists():
            missing_files.append(file)

    if missing_files:
        print(f"目录 '{directory}' 中缺少以下文件:")
        for file in missing_files:
            print(f"- {file}")


def check_subdirectories(main_directory):
    main_path = Path(main_directory)

    for subdirectory in main_path.iterdir():
        if subdirectory.is_dir():
            check_files(subdirectory)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python check.py <主目录路径>")
        sys.exit(1)

    main_directory = sys.argv[1]
    check_subdirectories(main_directory)
