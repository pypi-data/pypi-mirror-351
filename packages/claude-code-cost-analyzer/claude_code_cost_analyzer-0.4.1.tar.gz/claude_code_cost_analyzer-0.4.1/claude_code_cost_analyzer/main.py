"""Claude Code Cost Analyzer メインエントリーポイント

このモジュールはアプリケーションのメインエントリーポイントです。
コマンドライン引数の解析から出力まで、全体の処理フローを制御します。
"""

import sys
import logging
from typing import Optional, List

from .cli import parse_arguments
from .config import load_config, validate_config, ConfigError
from .collector import collect_log_files
from .parser import parse_multiple_log_files, LogParseError
from .aggregator import aggregate_data, AggregationError
from .formatter import format_data, FormatterError
from .exchange import get_exchange_rate, ExchangeRateError
from .models import ProcessedLogEntry


def setup_logging(verbose: bool = False) -> None:
    """ログ設定をセットアップする"""
    if verbose:
        # デバッグモード: 詳細なログを表示
        level = logging.DEBUG
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    else:
        # 通常モード: 重要なメッセージのみ表示
        level = logging.WARNING
        format_str = "%(message)s"
    logging.basicConfig(level=level, format=format_str, datefmt="%Y-%m-%d %H:%M:%S")


def filter_entries_by_date_range(
    entries: List[ProcessedLogEntry], start_date: Optional[str] = None, end_date: Optional[str] = None
) -> List[ProcessedLogEntry]:
    """日付範囲でエントリをフィルタリングする"""
    if not start_date and not end_date:
        return entries

    filtered_entries = []
    for entry in entries:
        entry_date = entry.date_str

        # 開始日のチェック
        if start_date and entry_date < start_date:
            continue

        # 終了日のチェック
        if end_date and entry_date > end_date:
            continue

        filtered_entries.append(entry)

    return filtered_entries


def get_exchange_rate_for_currency(
    target_currency: str, api_key: Optional[str] = None, config: Optional[dict] = None
) -> Optional[float]:
    """指定通貨表示用の為替レートを取得する"""
    try:
        # 設定ファイルからAPIキーを取得（コマンドライン引数が優先）
        if not api_key and config:
            api_key = config.get("exchange_rate_api_key")

        return get_exchange_rate(from_currency="USD", to_currency=target_currency, api_key=api_key)
    except ExchangeRateError as e:
        logging.warning(f"為替レート取得に失敗しました ({target_currency}): {e}")
        return None


def main() -> int:
    """メインエントリーポイント

    Returns:
        int: 終了コード (0: 成功, 1: エラー)
    """
    logger = None
    try:
        # 1. コマンドライン引数の解析
        args = parse_arguments()

        # ログ設定
        setup_logging(verbose=args.debug)

        logger = logging.getLogger(__name__)
        if args.debug:
            logger.info("Claude Code Cost Analyzer を開始します")

        # 2. 設定ファイルの読み込み
        try:
            config = load_config(config_path=str(args.config) if args.config else None)
            validate_config(config)
            logger.debug("設定ファイルを正常に読み込みました")
        except ConfigError as e:
            logger.error(f"設定エラー: {e}")
            return 1

        # 3. ログファイルの収集
        try:
            log_directory = args.directory
            if args.debug:
                logger.info(f"ログファイルを収集中: {log_directory}")
            log_files = collect_log_files(log_directory)

            if not log_files:
                if args.debug:
                    logger.warning(f"ログファイルが見つかりませんでした: {log_directory}")
                print("ログファイルが見つかりませんでした。")
                return 0

            if args.debug:
                logger.info(f"{len(log_files)} 個のログファイルを発見しました")
        except (FileNotFoundError, PermissionError, ValueError) as e:
            logger.error(f"ログファイル収集エラー: {e}")
            print(f"エラー: {e}")
            return 1

        # 4. ログデータの解析（タイムゾーン考慮）
        timezone = args.timezone or config.get("timezone", "auto")
        try:
            if args.debug:
                logger.info(f"ログファイルを解析中... (timezone: {timezone})")
            all_entries = parse_multiple_log_files(log_files, target_timezone=timezone)

            if not all_entries:
                if args.debug:
                    logger.warning("解析可能なログエントリが見つかりませんでした")
                print("解析可能なログエントリが見つかりませんでした。")
                return 0

            if args.debug:
                logger.info(f"{len(all_entries)} 個のログエントリを解析しました")
        except LogParseError as e:
            logger.error(f"ログ解析エラー: {e}")
            print(f"ログ解析エラー: {e}")
            return 1

        # 5. 日付範囲でのフィルタリング
        # デフォルト日付範囲の適用
        start_date = args.start_date
        end_date = args.end_date
        if not start_date and not end_date and not args.all_data:
            # デフォルト日付範囲を適用（--all-dataが指定されていない場合）
            default_range_days = config.get("default_date_range_days", 30)
            if default_range_days > 0:
                from datetime import date, timedelta

                end_date = date.today().strftime("%Y-%m-%d")
                start_date = (date.today() - timedelta(days=default_range_days)).strftime("%Y-%m-%d")
                if args.debug:
                    logger.info(f"デフォルト日付範囲を適用: {start_date} から {end_date} ({default_range_days}日間)")

        if args.all_data and args.debug:
            logger.info("全データを表示します（日付範囲フィルタ無効）")
        if start_date or end_date:
            if args.debug:
                logger.info("日付範囲でフィルタリング中...")
            filtered_entries = filter_entries_by_date_range(all_entries, start_date, end_date)
            if args.debug:
                logger.info(f"フィルタリング後: {len(filtered_entries)} エントリ")
            all_entries = filtered_entries

            if not all_entries:
                if args.debug:
                    logger.warning("指定された日付範囲にログエントリが見つかりませんでした")
                print("指定された日付範囲にログエントリが見つかりませんでした。")
                return 0

        # 6. 通貨変換のための為替レート取得
        exchange_rate = None
        target_currency = None
        if args.currency:
            target_currency = args.currency
            if args.debug:
                logger.info(f"為替レートを取得中... (USD -> {target_currency})")
            exchange_rate = get_exchange_rate_for_currency(
                target_currency=target_currency, api_key=args.exchange_rate_api_key, config=config
            )
            if exchange_rate is None:
                if args.debug:
                    logger.warning(f"為替レートの取得に失敗しました。{target_currency}表示は無効になります。")
                target_currency = None
            else:
                if args.debug:
                    logger.info(f"為替レート USD/{target_currency}: {exchange_rate}")

        # 7. データ集計
        try:
            if args.debug:
                logger.info(f"データを{args.granularity}単位で集計中...")
            aggregated_data = aggregate_data(
                all_entries,
                granularity=args.granularity,
                exchange_rate=exchange_rate,
                target_currency=target_currency,
                sort_by=args.sort,
                sort_desc=args.sort_desc,
            )
            if args.debug:
                logger.info("データ集計が完了しました")
        except (AggregationError, ValueError) as e:
            logger.error(f"データ集計エラー: {e}")
            print(f"データ集計エラー: {e}")
            return 1

        # 8. 出力フォーマット
        try:
            if args.debug:
                logger.info(f"{args.output}形式で出力を生成中...")
            output = format_data(
                data=aggregated_data,
                output_format=args.output,
                granularity=args.granularity,
                target_currency=target_currency,
                limit=args.limit,
                sort_by=args.sort,
                sort_desc=args.sort_desc,
            )

            # 結果出力
            print(output)
            if args.debug:
                logger.info("処理が正常に完了しました")

        except FormatterError as e:
            logger.error(f"出力フォーマットエラー: {e}")
            print(f"出力フォーマットエラー: {e}")
            return 1

        return 0

    except KeyboardInterrupt:
        if logger:
            logger.info("ユーザーによって処理が中断されました")
        print("\n処理が中断されました。")
        return 1

    except Exception as e:
        if logger:
            logger.error(f"予期しないエラーが発生しました: {e}", exc_info=True)
        print(f"予期しないエラー: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
