import os
import sys
from jack_tokenizer import JackTokenizer


def analyze_file(file_path):
    tokenizer = JackTokenizer(file_path)
    xml_file_path = file_path.replace(".jack", ".xml")
    tokenizer.output_xml(xml_file_path)


def analyze_directory(directory_path):
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".jack"):
                file_path = os.path.join(root, file)
                analyze_file(file_path)


def main():
    if len(sys.argv) != 2:
        print("Usage: python jack_analyzer.py <file_or_directory>")
        sys.exit(1)

    path = sys.argv[1]
    if os.path.isfile(path):
        analyze_file(path)
    elif os.path.isdir(path):
        analyze_directory(path)
    else:
        print(f"Error: {path} is not a valid file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main()
