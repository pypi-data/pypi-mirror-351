import os
import sys
import mimetypes
import chardet
import re

def is_text_file(file_path):
    mimetypes.init()
    mime_type, _ = mimetypes.guess_type(file_path)
    # Recognize .md files explicitly as text files
    if file_path.lower().endswith('.md'):
        return True
    return mime_type and mime_type.startswith('text/')

def should_include_file(file_name):
    # Exclude hidden files and files with specific extensions
    excluded_patterns = r'^\..*|.*\.(pyc|pyo|pyd|dll|exe|obj|o)$'
    return not re.match(excluded_patterns, file_name, re.IGNORECASE)

def get_file_list(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if should_include_file(file):
                file_path = os.path.join(root, file)
                if is_text_file(file_path):
                    file_list.append(file_path)
    return file_list

def detect_encoding(file_path):
    try:
        with open(file_path, 'rb') as file:
            result = chardet.detect(file.read())
        return result['encoding'] or 'utf-8'
    except IOError as e:
        print(f"Error reading file {file_path}: {e}")
        return 'utf-8'

def create_prompt_file(directory, file_list):
    prompt_file = os.path.join(directory, 'prompt.txt')
    try:
        with open(prompt_file, 'w', encoding='utf-8') as outfile:
            for file_path in file_list:
                rel_path = os.path.relpath(file_path, directory)
                outfile.write(f"{rel_path}:\n")
                encoding = detect_encoding(file_path)
                try:
                    with open(file_path, 'r', encoding=encoding) as infile:
                        for line in infile:
                            outfile.write(line)
                    outfile.write("\n\n")
                except IOError as e:
                    print(f"Error reading file {file_path}: {e}")
                except UnicodeDecodeError:
                    print(f"Error decoding file {file_path} with encoding {encoding}")
    except IOError as e:
        print(f"Error creating prompt file: {e}")
        sys.exit(1)

def get_user_confirmation(message):
    while True:
        response = input(message).lower()
        if response in ['y', 'n']:
            return response == 'y'
        print("Invalid input. Please enter 'y' or 'n'.")

def create_split_prompt_files(directory, file_list, split_count):
    files_per_split = len(file_list) // split_count
    remainder = len(file_list) % split_count
    
    start_idx = 0
    for i in range(split_count):
        # 各分割のファイル数を計算
        chunk_size = files_per_split + (1 if i < remainder else 0)
        end_idx = start_idx + chunk_size
        
        # 分割されたファイルリストを取得
        chunk_files = file_list[start_idx:end_idx]
        prompt_file = os.path.join(directory, f'prompt_{i+1}.txt')
        
        # 各プロンプトファイルを作成
        try:
            with open(prompt_file, 'w', encoding='utf-8') as outfile:
                for file_path in chunk_files:
                    rel_path = os.path.relpath(file_path, directory)
                    outfile.write(f"{rel_path}:\n")
                    encoding = detect_encoding(file_path)
                    try:
                        with open(file_path, 'r', encoding=encoding) as infile:
                            for line in infile:
                                outfile.write(line)
                        outfile.write("\n\n")
                    except IOError as e:
                        print(f"Error reading file {file_path}: {e}")
                    except UnicodeDecodeError:
                        print(f"Error decoding file {file_path} with encoding {encoding}")
        except IOError as e:
            print(f"Error creating prompt file: {e}")
            sys.exit(1)
            
        start_idx = end_idx

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Convert source files to prompt files')
    parser.add_argument('directory', help='Target directory or "here" for current directory')
    parser.add_argument('--cut', type=int, help='Split output into specified number of files')
    
    args = parser.parse_args()
    
    if args.directory == 'here':
        directory = os.getcwd()
    else:
        directory = args.directory
    
    if not os.path.isdir(directory):
        print(f"{directory} is not a valid directory.")
        sys.exit(1)
    
    file_list = get_file_list(directory)
    if not file_list:
        print(f"No text files found in {directory}")
        sys.exit(1)
    
    if len(file_list) > 50:
        message = "You are attempting to combine more than 50 files. Do you want to continue? (y/n): "
        if not get_user_confirmation(message):
            print("Operation cancelled.")
            sys.exit(0)
    
    if args.cut and args.cut > 0:
        create_split_prompt_files(os.path.abspath(directory), file_list, args.cut)
        print(f"Created {args.cut} prompt files in: {os.path.abspath(directory)}")
    else:
        create_prompt_file(os.path.abspath(directory), file_list)
        print(f"Prompt file created: {os.path.join(os.path.abspath(directory), 'prompt.txt')}")

if __name__ == '__main__':
    main()