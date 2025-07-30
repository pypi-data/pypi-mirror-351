# 要件とタスクリスト
実行時はまずを以下を読み込み内容を把握する事

bank/basic_design_document.md
bank/todos_overview.yaml
bank/implement_steps.yaml




# 計画の立案
- 実行する task を把握し, まずは計画を立案する事



# 開発コマンド
- uv を用いる事



# コードの修正後
- document を修正内容を反映すること.
    - 不要な部分は適宜削除すること.
- test に修正内容を反映する事.
- 以下を実行し, 正常であるか確認する事
    - pytest
    - black
    - flake8
    - mypy



# テスト関連
## 結合テスト (Integration Tests)
- 場所: `tests/integration/`
- 実行: `uv run python -m pytest tests/integration/ -v`
- 46のテストでエンドツーエンド動作を検証
- テストデータ: `tests/integration/test_data/`（総コスト$0.241、総トークン6,900）
- カバー範囲: 全出力形式、集計単位、日付フィルタ、エラーハンドリング
- 詳細は `tests/integration/README.md` を参照

## ユニットテスト
- 場所: `tests/`
- 実行: `uv run python -m pytest tests/ -v`
- 各モジュールの個別機能をテスト

## テスト実行のベストプラクティス
- 新機能追加時は対応する結合テストも追加
- テストデータ変更時は期待値も更新
- エラーケースのテストも忘れずに実装

# Release作業手順
## バージョン更新対象ファイル
1. `pyproject.toml` - version フィールド (現在: 0.4.4)
2. `claude_code_cost_analyzer/__init__.py` - __version__ 変数
3. `tests/integration/test_end_to_end.py` - バージョンテストの期待値
4. `CHANGELOG.md` - 新バージョンのエントリ追加

**重要**: バージョン変更時は上記4ファイル全ての更新が必要です

## Release手順
1. バージョン番号の統一確認
   - pyproject.toml と __init__.py のバージョンが一致していること
2. 説明文の言語統一
   - __init__.py の description を英語に統一
3. CHANGELOG.md の更新
   - 新バージョン `## [X.Y.Z] - YYYY-MM-DD` セクションを追加
   - `### Added`, `### Changed`, `### Fixed`, `### Documentation` セクションで変更内容を整理
   - 具体的な変更内容を記述（ユーザー視点での利点を含む）
4. テスト実行
   - `uv run python -m pytest tests/ -v`
   - `uv run black .`
   - `uv run flake8`
   - `uv run mypy claude_code_cost_analyzer/`
5. ビルドとパッケージング
   - `uv build`
6. Git操作
   - コミット作成
   - タグ作成 (v{version})
   - Push
