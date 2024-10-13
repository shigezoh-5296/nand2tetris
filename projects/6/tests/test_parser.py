import os
import sys
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from src.parser import Parser


# テスト用のファイルを作成するヘルパー関数
def create_test_file(directory, filename, content):
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, filename), 'w') as f:
        f.write(content)


# テスト用のファイルとディレクトリを設定
TEST_DIR = 'C:/work/nand2tetris/nand2tetris/projects/6/test_files'
TEST_FILE = 'test.asm'
TEST_CONTENT = """
// This is a comment
@2
D=A  // D = 2
@3       
M=D+A
@LOOP
D;JEQ
0;JMP
"""


@pytest.fixture(scope='module')
def setup_test_files():
    create_test_file(TEST_DIR, TEST_FILE, TEST_CONTENT)
    yield
    # テスト後にファイルを削除
    os.remove(os.path.join(TEST_DIR, TEST_FILE))
    os.rmdir(TEST_DIR)


def test_find_file(setup_test_files):
    parser = Parser(TEST_FILE, root_dir=TEST_DIR)
    assert parser.filepath == os.path.join(TEST_DIR, TEST_FILE)


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        Parser('non_existent_file.asm', root_dir=TEST_DIR)


def test_get_lines(setup_test_files):
    parser = Parser(TEST_FILE, root_dir=TEST_DIR)
    expected_lines = ['@2', 'D=A', '@3', 'M=D+A', '@LOOP', 'D;JEQ', '0;JMP']
    assert parser.lines == expected_lines


def test_advance(setup_test_files):
    parser = Parser(TEST_FILE, root_dir=TEST_DIR)
    parser.advance()
    assert parser.current_command == '@2'
    parser.advance()
    assert parser.current_command == 'D=A'


def test_has_more_commands(setup_test_files):
    parser = Parser(TEST_FILE, root_dir=TEST_DIR)
    assert parser.has_more_commands() == True
    while parser.has_more_commands():
        parser.advance()
    assert parser.has_more_commands() == False


def test_symbol(setup_test_files):
    parser = Parser(TEST_FILE, root_dir=TEST_DIR)
    parser.advance()
    assert parser.symbol() == '2'
    parser.advance()
    with pytest.raises(ValueError):
        parser.symbol()


def test_dest(setup_test_files):
    parser = Parser(TEST_FILE, root_dir=TEST_DIR)
    parser.advance()
    parser.advance()
    assert parser.dest() == 'D'
    parser.advance()
    parser.advance()
    assert parser.dest() == 'M'


def test_comp(setup_test_files):
    parser = Parser(TEST_FILE, root_dir=TEST_DIR)
    parser.advance()
    parser.advance()
    parser.advance()
    parser.advance()
    assert parser.comp() == 'D+A'


def test_jump(setup_test_files):
    parser = Parser(TEST_FILE, root_dir=TEST_DIR)
    parser.advance()
    parser.advance()
    parser.advance()
    parser.advance()
    parser.advance()
    parser.advance()
    assert parser.jump() == 'JEQ'
    parser.advance()
    assert parser.jump() == 'JMP'


if __name__ == '__main__':
    pytest.main()
