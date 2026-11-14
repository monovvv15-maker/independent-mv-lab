# V23 一括進行報告｜えがちゃんへ 30秒MV
## 完了
- Pexelsの公開実動画6件をGitHub Actionsで一時取得し、各3フレーム抽出。元動画は実行後削除。
- 実見で、黒い靴と白い靴の人物不一致、雨の分かりにくさを検出。白靴で歩く映像（Pexels 4464905）と水たまり（Pexels 13749224）へ差し替え。
- 6素材・総尺30秒の暫定EDLをv23_prelaunch.pyに固定。
- 無音映像だけを合成するv23_video_only.py、非公開MP3を後付けするv23_private_mux.pyを実装。
- 動画合成は明示的な許可フラグ必須。動画自動生成は無効。
- GitHub Actions 62テスト合格。制作前エラー0件。ただし歌詞同期・画質の完成合格ではない。
- 不要なpush自動調査は停止し、無料Actions枠の節約運用へ。
## 検証リンク
- V21 6映像: https://github.com/monovvv15-maker/independent-mv-lab/actions/runs/43544131874
- V22 差し替え: https://github.com/monovvv15-maker/independent-mv-lab/actions/runs/43544406541
- V22B 白靴歩行: https://github.com/monovvv15-maker/independent-mv-lab/actions/runs/43544608725
- V23 prelaunch: https://github.com/monovvv15-maker/independent-mv-lab/actions/runs/43544991449
## 未確認・重要
- 原曲歌詞の厳密なタイムスタンプは未確定。最初の30秒は粗編集と明記。
- 6素材が違う撮影環境のため、全尺での光・人物・カメラ連続性は未確認。
- MP4はまだ一度も生成していない。承認後に実映像を見て評価する。
- 公開GitHubに原曲音声を保存しない。
## 次のユーザー操作
- 今は不要。試写生成へ進める場合のみ『動画生成開始』と言う。
- GitHub手動起動が連携上できない場合に限り、ActionsのYES入力を1回お願いする。