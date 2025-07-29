import argparse
from pathlib import Path

from ..utils import zip_modules


def main():
    parser = argparse.ArgumentParser(description="Zip Module")
    parser.add_argument(
        "python_package_name", type=str, help="Path to the file to be zipped"
    )
    parser.add_argument("output_file", type=str, help="Output zip file name")
    args = parser.parse_args()

    data = zip_modules(
        [args.python_package_name],
    )
    Path(args.output_file).write_bytes(data)


if __name__ == "__main__":
    main()
