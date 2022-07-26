# 取扱説明書
## 注意事項
- チャット量に応じて半日とか1日とか3日とかかかります。
- その間パソコンつけっぱなしになります。

## 事前準備
- リポジトリをクローン(このページの右上あたりにある緑の「Code」ボタン押して「Download ZIP」するなど)
- Anacondaのインストール(「anaconda python」とかで検索)
- Anaconda Promptを開き、以下コマンドを実行
  - `cd /d lo_to_ba`
    - パスの指定は自分の環境次第(lo_to_ba-masterとか)
  - `conda create -y -n lo_to_ba_py39 -c conda-forge python=3.9 --file requirements.txt`
    - Anaconda Promptへのペーストは「Shift + insert」
  - `conda activate lo_to_ba_py39`
  - `pip install chromedriver-binary==103.0.5060.134`
    - PCにインストールされているgoogle chromeのバージョンと合わせる必要あり
  - `pip install pycryptodome`

## 実行手順
### 手順1.参加しているプライベートグループリストを作成
- ログインタイプに従って以下のどれかを実行する
  - `python bin\lobi\create_private_group_list.py --login_by twitter`
    - 20秒弱かかる
  - `python bin\lobi\create_private_group_list.py --login_by lobi`
  - `python bin\lobi\create_private_group_list.py --login_by lobi_unhidden`
- 実行すると以下を聞かれるので入力する
  - ログイン情報の暗号化用パスワード(AES暗号化するため)(覚えておくこと)(短めでOK)
  - ログイン情報の確認用パスワード
    - 忘れたらlo_to_ba/certification/以下のファイルを削除してもう一度IDとパスワードを入力すればOK
  - lobiまたはtwitterへのログインIDまたはemailアドレス
  - lobiまたはtwitterへのログインパスワード  
- 「ログイン失敗」と出た場合
  - 上記コマンドを正しくやり直す
  - パスワードのコピーペーストで失敗している可能性あるので直打ちもしてみる
- 「全て完了」と出た場合
  - 以下2つのファイルができている
    - lo_to_ba/output/joining_private_groups.csv
      - 参加しているグループ一覧、編集用
    - lo_to_ba/output/original_joining_private_groups.csv
      - 参加しているグループ一覧、閲覧用
    - lo_to_ba/output/joining_private_groups.json
      - 参加しているグループメタ情報

### 手順2.保存したいグループの編集
  - lo_to_ba/output/joining_private_groups.csvを右クリック編集して保存したいグループのみに絞る

### 手順3.グループのチャット等を保存*時間かかる
- ログインタイプに従って以下のどれかを実行する
  - `python bin\lobi\save_private_group_chats.py --login_by twitter`
  - `python bin\lobi\save_private_group_chats.py --login_by lobi`
  - `python bin\lobi\save_private_group_chats.py --login_by lobi_unhidden`
- 実行すると以下を聞かれるので入力する
  - ログイン情報の暗号化用パスワード(手順1で作成したもの)
  - ログイン情報の確認用パスワード
    - 忘れたらlo_to_ba/certification/以下のファイルを削除してもう一度IDとパスワードを入力すればOK
- 「ログイン失敗」と出た場合
  - 上記コマンドを正しくやり直す
- 「全て完了」と出た場合
  - lo_to_ba/output/[グループ名]以下に色々バックアップが取れている

## 実行結果
- 主な保存ファイルは「output/グループ名/chat_[グループ名].json」  
dictの主な構成要素は以下
  - ["user"]["name"]  # 書き込みユーザー名
  - ["user"]["icon_path"]  # ユーザーアイコン
  - ["user"]["cover_path"]  # ユーザー背景
  - ["message"]  # 投稿文章
  - ["assets"][i]["saved_path"]  #投稿画像
  - ["reply_to"]  # 新トピか返信か。nullなら新トピ
  - ["created_date_jp"]  # 書き込み日本時刻
  - ["full_replies"][j]  # 返信。dictの構成は上記と同じ
- 画像はoutput/グループ名/img以下
  - chat  # 書き込みに添付の画像
  - group  # グループのアイコンと背景(あれば)
  - user/cover  # ユーザーの背景
  - user/icon  # ユーザーのアイコン

## 復元方法
- まだ
- 近いうちに

## 簡単なプログラムアップデート方法
- zipをダウンロードしてダウンロードフォルダで展開
- ファイルを全てコピー
- 実行フォルダに上書き貼り付け
  - outputフォルダはzipに含まれていないので干渉しない

## 補足
### プログラム実行中も自由にパソコン触っていい
### このプログラムを並列で実行してはいけない
### ログ
lo_to_ba/log/log  
コマンド実行する度にリセットされるため注意  
エラーが発生した場合は先にlogのコピーを取って新しいコマンドを実行するなど

### Anaconda Promptを開き直した場合
- 環境は既にあるのでAnaconda Promptを開き、以下コマンドのみを実行
  - cd /d lo_to_ba
    - パスの指定は自分の環境次第
  - conda activate lo_to_ba_py39  
  - 手順3を実行

### 途中から再開したい場合
- lo_to_ba/output/joining_private_groups.csvをメモ帳などで編集し、既に保存が完了しているグループの行を削除
- 手順3を実行

### 途中で止めたい場合
- Anaconda Promptで「Ctrl + c」

### 意味不明のエラーが出た場合
- requestsのretry機能実装してないせいかも。
- もう一回やればうまくいくかも。

### 前回取得時からのアップデートを取得したいとき
- 差分バックアップ機能は無い
- lo_to_ba/outputのディレクトリ名を変更しバックアップ
- 手順1から新規取得を開始する

## 更新履歴
### 2022/07/26
- AES暗号化対応
  - `pip install pycryptodome`が必要
  - 初回起動時にログイン情報の暗号化用パスワード(短め)+ログイン情報の入力が必要
  - 2回目以降はログイン情報の暗号化用パスワード(短め)のみでOK
- グループ名等のエスケープ強化
- ConnectionResetError対応
  - requests_wait_timeを2倍にして待機後再度同じメソッドを実行
  - max_requests_wait_time以上になるとraise eして終了
