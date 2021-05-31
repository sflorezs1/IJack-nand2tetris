import sys
import os
from ijkcompilationengine import IjkCompilationEngine


def compile_file(file_path: str) -> None:
    with open(file_path, 'r') as ifile:
        file_name: str = os.path.basename(file_path)
        file_path_no_ext, _ = os.path.splitext(file_path)
        file_name_no_ext, _ = os.path.splitext(file_name)

        ofile_path = file_path_no_ext + '.vm'
        with open(ofile_path, 'w') as ofile:
            compiler: IjkCompilationEngine = IjkCompilationEngine(ifile, ofile)
            compiler.compile_class()


def compile_directory(dir_path: str) -> None:
    for file in os.listdir(dir_path):
        file_path: str = os.path.join(dir_path, file)
        _, file_ext = os.path.splitext(file_path)
        if os.path.isfile(file_path) and file_ext.lower() == '.ijk':
            compile_file(file_path)


def main() -> None:
    if len(sys.argv) < 2:
        print('usage: IjkCompiler (file|dir)')
        sys.exit(1)

    input_path = sys.argv[1]

    if os.path.isdir(input_path):
        compile_directory(input_path)
    elif os.path.isfile(input_path):
        compile_file(input_path)
    else:
        print("Invalid file/directory, compilation failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
