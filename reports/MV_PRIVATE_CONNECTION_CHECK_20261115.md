# 連続制作基盤 V1｜Dropbox実接続チェック（2026-11-15）

## 実行
- GitHub Actions: https://github.com/monovvv15-maker/independent-mv-lab/actions/runs/43680325146
- 読取専用検査。動画・画像生成、素材のDL、公開Artifact作成、権限変更なし。
- `test_mv_private_connection_check.py` テスト成功。
- 接続ジョブは**失敗（想定したFail closed）**。理由：GitHub Actionsの下記6項目すべて未設定。
  - Secrets: `DROPBOX_REFRESH_TOKEN` / `DROPBOX_APP_KEY` / `DROPBOX_APP_SECRET`
  - Variables: `MV_JACKET_DROPBOX_PATH` / `MV_AUDIO_DROPBOX_PATH` / `MV_PRIVATE_CACHE_PATH`
- このチェックで未設定なのは**GitHub Actionsの対象リポジトリにおける環境**。ユーザーの個別Dropbox連携や他リポジトリまで未設定と断定しない。
- Dropbox連携で `/Suilemo/MV` を一覧確認。Fullerene、PINK_100TEN、SHIAWASE_JIGOKUほか既存フォルダはあるが、`えがちゃんへ` 原曲とジャケットは今回の検索/探索では未発見。
- 公開リポジトリのため、原曲やジャケットをコミット、公開Artifactへ保存しない。

## ひとつの初期設定手順
1. 原曲MP3とジャケット原本を作成者の**非公開Dropbox**に保存。既存ファイルがあれば移動/複製不要、既存パスを使う。
2. GitHubの `monovvv15-maker/independent-mv-lab` → Settings → Secrets and variables → Actions で、Dropboxアプリの**既存の有効な**Refresh Token/App Key/App SecretをSecretsへ設定。チャットに秘密値は貼らない。
3. 同じ画面のVariablesへ画像と音源の正確なDropboxパス、専用のキャッシュZIP保存先パスを設定。
4. Actions → `MV private Dropbox metadata connection check - NO VIDEO` → Run workflow を1回起動。
5. `ready:true` を確認して初めて接続済みと判断。まだ動画は作らない。

## 安全ゲート
- SecretsとVariablesがなければ早期停止。
- 動画作成を伴うワークフロー `Repeatable MV private production - explicit author approval only` は別物。`confirm_video_generation=YES` は作成者による動画生成の承認時だけ入力。
- 検証ログにトークンや生データは出力しない。

## 状態
完了：共通制作エンジン、テスト、読み取り接続チェック。
未完了：GitHub Secrets/Variables設定、元画像/原曲の私有Dropbox保存場所確認、実OAuth/パスメタデータ検査。
未確認：本番全編1回実行時の無料枠/Dropbox保存と再開実績。
