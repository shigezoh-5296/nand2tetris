import os
import sys
from jack_tokenizer import JackTokenizer
from compilation_engine import CompilationEngine
from symbol_table import SymbolTable
from vm_writer import VMWriter


def analyze_file(file_path):
    tokenizer = JackTokenizer(file_path)
    st = SymbolTable()
    vm_file_path = file_path.replace(".jack", ".vm")
    vw = VMWriter(vm_file_path)
    ce = CompilationEngine(tokenizer, st, vw)
    ce.compile()
    vw.close()
    print(f"Analyzed {file_path} and generated {vm_file_path}")


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
