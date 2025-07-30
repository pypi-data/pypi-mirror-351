"""Claude Code Cost Analyzer パッケージ実行エントリーポイント

このモジュールは `python -m claude_code_cost_analyzer` コマンドで実行される際のエントリーポイントです。
メインモジュールのmain()関数を呼び出し、適切な終了コードでプログラムを終了させます。
"""

import sys
from .main import main

if __name__ == "__main__":
    sys.exit(main())
