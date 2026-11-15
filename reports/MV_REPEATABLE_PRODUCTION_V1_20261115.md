# MV連続制作基盤 V1｜独立MV Lab

制作責任者承認：2026-11-15「うん」。対象：制作基盤の調査・実装・QAのみ。**V44動画生成の追加承認ではない。**

## 目的
「確認→承認→報告」を何度も繰り返さず、作成者が**一度「動画生成開始」と承認したら**、1回のGitHub Actionsで次を実行する。

```
制作レシピ・台本
  ↓ 私有ジャケット/原曲のSHA照合
[preflight]
  ↓
[render] 720x720 H.264 無音マスター
  ↓
[mux] 私有の原曲と同期・AAC付与
  ↓
[verify] 尺・コーデック・音声ありなし・品質レポート
  ↓
[package] iPhone版540×540と高画質版
  ↓
非公開Dropboxに保存 / ステージ別SHA付きreceiptで再開
```

### 既存エンジンを守る
- V38/V40：正式台本、不変更
- V39/V41/V42：既存の描画・下書き・描き直し・歌詞停止処理を再利用
- V43：既存の完成物は上書きしない
- V44：基盤確認後まで動画生成保留
- 既存世代別Actionsは削除しない

## 本体
- `mv_repeatable_pipeline.py`：preflight→render→mux→verify→package を実行する。ステージごとに入力依存SHA、完了証跡と出力SHAを保存する。途中失敗の復旧は有効な段階をスキップする
- `mv_drawing_render.py`：V42の描画エンジンをH.264無音映像化するアダプタ
- `mv_private_dropbox.py`：非公開Dropboxから素材取得・プライベート再開アーカイブ保存
- `catalog/mv_repeatable_recipe_v1.json`：作業ごとの原本SHAとエンジンバージョン
- `.github/workflows/mv-repeatable-qa.yml`：無料GitHub Actionsで**映像生成せず**QA
- `.github/workflows/mv-repeatable-private-render.yml`：明示的承認時だけ手動起動する実制作Actions

## 公開Repoに関する重大なプライバシー条件
**このGitHubリポジトリはpublic。** 原曲・元画像・音声付き完成MP4・生成途中のメディアをコミット・GitHub Artifactsにアップロードしない。制作実行にはGitHub ActionsのSecretsとVariablesを一度設定し、私有Dropboxでのみ成果物を保存する設計。

### 1回限りの初期設定（値はリポジトリに書かない）
Actions Secrets：
- `DROPBOX_REFRESH_TOKEN`
- `DROPBOX_APP_KEY`
- `DROPBOX_APP_SECRET`

Actions Variables：
- `MV_JACKET_DROPBOX_PATH`（元画像の私有Dropboxパス）
- `MV_AUDIO_DROPBOX_PATH`（原曲MP3の私有Dropboxパス）
- `MV_PRIVATE_CACHE_PATH`（完成MP4と再開台帳を含むZIPを置く私有Dropboxパス。拡張子zip）

APIトークンはワークフローからログ出力しない。既存Dropbox秘密情報が正しいか、現在のツールからは読み取れない（変更は行わない）。Dropboxアプリの許可には `files.content.read`/`files.content.write` が必要な場合がある。

### 通常運用
1. 演出、レシピをGitHub上で変更し、読み取りだけのQAを実行する。承認は不要。
2. 作成者から明示的な**「動画生成開始」**を受領して初めて、`mv-repeatable-private-render.yml` を `workflow_dispatch` し、`confirm_video_generation` = `YES` とする。
3. Actionsが素材の一致を検証し、各段階をレンダリングする。ステージが既に成功していたらハッシュ一致を検証して再利用。
4. 私有Dropboxに生成物／報告／ステージ完了証跡を保存する。GitHub Actions Artifactは作らない。
5. 作成者はDropboxの私有納品から全編を評価する。技術QA合格と作品の合格を分ける。

### 限界・未確認
- GitHub ActionsとDropboxを使った**本当の全編実運転は未検証**。トークン・保存先は環境により未設定の可能性
- 一回の全編レンダリングでも無料Actionsの実行時間枠やDropboxデータ転送制限を超える場合がある
- キャッシュZIP 140MiB超はアップロードセッション方式へ拡張が必要
- 元画像・音源のSHAはレシピと一致必須
- 歌詞の厳密時刻は未確定。レンダリング成功でも歌詞同期の自動合格にはしない
- 現時点でこのパイプラインの**production rendererはえがちゃんへ/V42描画方式**。他曲・他スタイルへの展開はアダプター追加が必要
- 素材はGitHubに置かず非公開Dropboxに保持。Secrets値はGitHub APIから閲覧不可

## テスト
```sh
python -m unittest -v test_mv_repeatable_pipeline.py test_mv_private_dropbox.py
python mv_repeatable_pipeline.py --dry-run
```
どちらも画像・音声・動画は生成しない。テストは疑似データと台帳検証のみ。

## 報告の分類
- **完了**：コード実装、QA成功
- **未完了**：作成者承認によるプライベート全編テストとiPhone実機検証
- **未確認**：GitHub Secrets/Variables、Dropboxアプリの書込権限、全編の生成時間・品質

失敗を自動で「成功」に変えない。作成者の新しい動画承認がない限り、ビデオ出力を走らせない。
