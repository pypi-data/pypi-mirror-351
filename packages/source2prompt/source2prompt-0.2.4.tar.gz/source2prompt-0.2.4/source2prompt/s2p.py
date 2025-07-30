import os
import sys
import argparse
import charset_normalizer

# 許可する拡張子（網羅的なリスト）
ALLOWED_EXTENSIONS = {
    # プログラミング言語
    '.py', '.pyw', '.pyi',  # Python
    '.js', '.mjs', '.cjs', '.jsx',  # JavaScript
    '.ts', '.tsx', '.d.ts',  # TypeScript
    '.java', '.kt', '.kts', '.scala',  # JVM系
    '.cs', '.vb', '.fs',  # .NET系
    '.cpp', '.cc', '.cxx', '.c', '.h', '.hpp', '.hxx',  # C/C++
    '.rs',  # Rust
    '.go', '.mod', '.sum',  # Go
    '.php', '.phtml',  # PHP
    '.rb', '.rbw', '.rake', '.gemspec',  # Ruby
    '.swift',  # Swift
    '.m', '.mm', '.h',  # Objective-C
    '.dart',  # Dart
    '.lua',  # Lua
    '.pl', '.pm', '.t',  # Perl
    '.r', '.R', '.rmd',  # R
    '.jl',  # Julia
    '.ex', '.exs',  # Elixir
    '.erl', '.hrl',  # Erlang
    '.clj', '.cljs', '.cljc',  # Clojure
    '.hs', '.lhs',  # Haskell
    '.ml', '.mli',  # OCaml
    '.elm',  # Elm
    '.nim',  # Nim
    '.zig',  # Zig
    '.v', '.vh', '.sv', '.svh',  # Verilog/SystemVerilog
    '.vhd', '.vhdl',  # VHDL
    
    # Web関連
    '.html', '.htm', '.xhtml',
    '.css', '.scss', '.sass', '.less', '.styl',
    '.vue', '.svelte',
    '.asp', '.aspx', '.jsp',
    
    # シェルスクリプト
    '.sh', '.bash', '.zsh', '.fish', '.ksh', '.csh',
    '.ps1', '.psm1', '.psd1',  # PowerShell
    '.bat', '.cmd',  # Windows Batch
    
    # データ・設定ファイル
    '.json', '.json5', '.jsonl',
    '.xml', '.xsd', '.xsl', '.xslt',
    '.yaml', '.yml',
    '.toml',
    '.ini', '.cfg', '.conf', '.config',
    '.env', '.envrc',
    '.properties',
    '.plist',
    '.reg',
    
    # ドキュメント・マークアップ
    '.md', '.markdown', '.mdown', '.mkd',
    '.rst', '.rest',
    '.txt', '.text',
    '.rtf',
    '.tex', '.latex', '.ltx',
    '.org',
    '.adoc', '.asciidoc',
    '.wiki',
    
    # データベース・クエリ
    '.sql', '.mysql', '.pgsql', '.plsql',
    '.cypher',
    '.graphql', '.gql',
    
    # ビルド・依存関係
    '.gradle', '.gradle.kts',
    '.maven', '.pom',
    '.cmake', '.cmakelist',
    '.make', '.mk', '.makefile',
    '.bazel', '.bzl',
    '.dockerfile', '.containerfile',
    '.vagrantfile',
    '.procfile',
    
    # パッケージ管理
    '.package.json', '.package-lock.json',
    '.yarn.lock', '.pnpm-lock.yaml',
    '.pipfile', '.pipfile.lock',
    '.requirements.txt', '.requirements-dev.txt',
    '.poetry.lock', '.pyproject.toml',
    '.gemfile', '.gemfile.lock',
    '.cargo.toml', '.cargo.lock',
    '.go.mod', '.go.sum',
    
    # CI/CD・設定
    '.gitignore', '.gitattributes', '.gitconfig',
    '.dockerignore',
    '.editorconfig',
    '.eslintrc', '.eslintignore',
    '.prettierrc', '.prettierignore',
    '.stylelintrc',
    '.babelrc',
    '.npmrc', '.yarnrc',
    
    # その他
    '.log', '.out', '.err',
    '.diff', '.patch',
    '.asm', '.s',  # Assembly
    '.f', '.f90', '.f95', '.f03', '.f08',  # Fortran
    '.cob', '.cbl',  # COBOL
    '.pas', '.pp',  # Pascal
    '.ada', '.adb', '.ads',  # Ada
    '.tcl', '.tk',  # Tcl/Tk
    '.vbs', '.vba',  # VBScript
    '.awk',  # AWK
    '.sed',  # sed
    '.flex', '.l',  # Flex
    '.y', '.yacc',  # Yacc/Bison
}

# 明示的に除外する拡張子
EXCLUDED_EXTENSIONS = {
    # 画像ファイル
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
    '.svg', '.ico', '.webp', '.avif', '.heic', '.raw',
    '.psd', '.ai', '.eps', '.indd',
    
    # 動画・音声ファイル
    '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv',
    '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a',
    
    # アーカイブ・圧縮ファイル
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz',
    '.tar.gz', '.tar.bz2', '.tar.xz', '.tgz', '.tbz2',
    '.cab', '.msi', '.deb', '.rpm',
    
    # バイナリ・実行ファイル
    '.exe', '.dll', '.so', '.dylib', '.a', '.lib',
    '.obj', '.o', '.pyc', '.pyo', '.pyd',
    '.class', '.jar', '.war', '.ear',
    '.wasm',
    
    # オフィス文書
    '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.odt', '.ods', '.odp', '.pages', '.numbers', '.key',
    '.pdf',
    
    # フォント
    '.ttf', '.otf', '.woff', '.woff2', '.eot',
    
    # データベースファイル
    '.db', '.sqlite', '.sqlite3', '.mdb', '.accdb',
    
    # その他バイナリ
    '.bin', '.dat', '.dump', '.img', '.iso', '.dmg',
}

# 除外するディレクトリ
EXCLUDED_DIRECTORIES = {
    # Python
    '__pycache__', '.pytest_cache', '.mypy_cache', '.tox',
    'venv', '.venv', 'env', '.env',
    '.virtualenv', 'virtualenv',
    'site-packages', 'dist-packages',
    'build', 'dist',
    
    # Node.js
    'node_modules', '.npm', '.yarn', '.pnp',
    
    # Version Control
    '.git', '.svn', '.hg', '.bzr',
    
    # IDEs
    '.vscode', '.idea', '.vs', '.eclipse',
    '.sublime-project', '.sublime-workspace',
    
    # Rust
    'target',
    
    # Go
    'vendor',
    
    # Java
    '.gradle', '.m2', 'out',
    
    # .NET
    'bin', 'obj', 'packages',
    
    # Ruby
    '.bundle',
    
    # PHP
    '.composer',
    
    # Temporary/Cache
    'tmp', 'temp', '.tmp', '.temp',
    'cache', '.cache', 'caches',
    'logs', '.logs',
    
    # Coverage/Testing
    'coverage', '.coverage', '.nyc_output',
    'htmlcov', 'cov_html',
    
    # Documentation builds
    '_build', 'site',
}

def is_binary_file(file_path, chunk_size=8192):
    """ファイル先頭をチェックしてバイナリファイルを判定"""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(chunk_size)
            if not chunk:
                return False
                
            # NULL文字があればバイナリ
            if b'\x00' in chunk:
                return True
                
            # 制御文字の割合をチェック
            control_chars = sum(1 for b in chunk if b < 32 and b not in [9, 10, 11, 12, 13])
            if len(chunk) > 0 and control_chars / len(chunk) > 0.1:
                return True
                
    except Exception:
        return True
    return False

def should_exclude_directory(dir_path):
    """ディレクトリパスが除外対象かチェック"""
    path_parts = dir_path.replace('\\', '/').split('/')
    
    for part in path_parts:
        if part in EXCLUDED_DIRECTORIES:
            return True
        # .egg-info のようなパターンマッチング
        if part.endswith('.egg-info'):
            return True
    
    return False

def should_include_file(file_path):
    """ファイルパス全体を考慮して含めるべきかチェック"""
    # ディレクトリチェック
    dir_path = os.path.dirname(file_path)
    if should_exclude_directory(dir_path):
        return False
    
    file_name = os.path.basename(file_path)
    _, ext = os.path.splitext(file_name.lower())
    
    # 隠しファイルの除外（一部設定ファイルは許可）
    if file_name.startswith('.') and file_name.lower() not in {'.gitignore', '.gitattributes', '.editorconfig', '.eslintrc', '.prettierrc', '.stylelintrc', '.babelrc', '.npmrc', '.yarnrc'}:
        return False
    
    # 明示的に除外する拡張子
    if ext in EXCLUDED_EXTENSIONS:
        return False
    
    # 許可される拡張子
    if ext in ALLOWED_EXTENSIONS:
        return True
    
    # 拡張子なしのファイル（シェルスクリプトなど）
    if not ext:
        # よくある設定ファイル名
        config_files = {
            'dockerfile', 'containerfile', 'makefile', 'rakefile', 
            'gemfile', 'procfile', 'vagrantfile', 'jenkinsfile',
            'readme', 'license', 'changelog', 'contributing',
            'authors', 'contributors', 'maintainers'
        }
        if file_name.lower() in config_files:
            return True
        
        # バイナリファイルでなければ含める
        return not is_binary_file(file_path)
    
    return False

def is_text_file(file_path):
    """テキストファイルかどうかを判定（後方互換性のため残す）"""
    return should_include_file(file_path)

def get_file_list(directory, max_files=None):
    """ファイルリストを取得（改善版）"""
    file_list = []
    file_count = 0
    
    for root, dirs, files in os.walk(directory):
        # ディレクトリレベルでの除外
        dirs[:] = [d for d in dirs if not should_exclude_directory(os.path.join(root, d))]
        
        for file in files:
            file_path = os.path.join(root, file)
            if should_include_file(file_path):
                file_list.append(file_path)
                file_count += 1
                
                # 早期チェック機能
                if max_files and file_count >= max_files:
                    return file_list, True  # 制限に達したことを示すフラグ
    
    return file_list, False

def detect_encoding(file_path):
    """charset-normalizerを使用した高精度エンコーディング検出"""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            
        result = charset_normalizer.from_bytes(raw_data)
        if result.best():
            return result.best().encoding
        else:
            return 'utf-8'
    except Exception:
        return 'utf-8'

def create_prompt_file(directory, file_list):
    """プロンプトファイルを作成"""
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
    """ユーザー確認を取得"""
    while True:
        response = input(message).lower()
        if response in ['y', 'n']:
            return response == 'y'
        print("Invalid input. Please enter 'y' or 'n'.")

def create_split_prompt_files(directory, file_list, split_count):
    """分割プロンプトファイルを作成"""
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
    """メイン関数"""
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
    
    # まず50ファイルまでで早期チェック
    file_list, has_more = get_file_list(directory, max_files=50)
    
    if not file_list:
        print(f"No text files found in {directory}")
        sys.exit(1)
    
    # 50ファイル以上ある場合の確認
    if has_more:
        message = "More than 50 files found. Do you want to continue processing all files? (y/n): "
        if get_user_confirmation(message):
            # 全ファイルを取得
            file_list, _ = get_file_list(directory)
        else:
            print("Operation cancelled.")
            sys.exit(0)
    elif len(file_list) > 50:
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