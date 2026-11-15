# MV連続制作基盤 V1｜復旧試験と実接続の進捗（2026-11-15）

## 実施内容
- 対象：`monovvv15-maker/independent-mv-lab`（公開リポジトリ）
- `test_mv_resume_simulation.py` を追加し、仮データのみで **mux段階で意図的に失敗→既に完了済みのpreflight/renderを再利用→mux/verify/packageを実行→再実行では5工程すべて再利用** を検証
- 実際の音源・ジャケット・動画を使用せず、モックファイルのみで実施
- Actions: https://github.com/monovvv15-maker/independent-mv-lab/actions/runs/43680547810
- 42件自動テスト成功
- 元原本のアップロード・Dropbox書込・新規動画生成は行っていない

## 接続状態
- Dropbox内 `/Suilemo/MV` の一覧は可能（ChatGPT Dropbox接続）。
- しかし **GitHub Actions用の別個の設定6項目はすべて欠如**（前回接続テスト: https://github.com/monovvv15-maker/independent-mv-lab/actions/runs/43680325146 ）。
- 今回、GitHub Actions側の実Dropbox OAuth更新、画像・音源の存在照合、Dropboxへ非公開成果物の保存は未確認。
- 元画像・原曲の private Dropboxパスは未確認。確認できないまま仮パスを埋め込むことは禁止。
- この制作管理リポジトリが public なので、Secret値や個人の原本・音声付き動画をGitHubに登録しない。

## 状態
- **完了**：連続制作基盤コード、42件テスト、失敗工程の再開シミュレーション成功
- **未完了**：GitHub Actionsの既存Dropbox資格情報3件と素材／保存先パス3件の安全な登録
- **未確認**：OAuth実接続、私有Dropboxでの全編保存、V44での実動作
- **動画生成：実行していない**

## 次の必要な手動作業（1回のみ）
GitHub > independent-mv-lab > Settings > Secrets and variables > Actions:
- Secrets: `DROPBOX_REFRESH_TOKEN`, `DROPBOX_APP_KEY`, `DROPBOX_APP_SECRET`
- Variables: `MV_JACKET_DROPBOX_PATH`, `MV_AUDIO_DROPBOX_PATH`, `MV_PRIVATE_CACHE_PATH`

安全のため秘密値をチャットに貼らない。ユーザーが設定した後に `MV private Dropbox metadata connection check - NO VIDEO` を1回起動し、read-only で ready=true を確認する。
