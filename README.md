# 取扱説明書
## 事前準備
- リポジトリをクローン(下記URLの右上あたりにある緑の「Code」ボタン押して「Download ZIP」するなど)
  - https://github.com/minasonsuki/lo_to_ba
- Anacondaのインストール(「anaconda python」とかで検索)
- Anaconda Promptを開き、以下コマンドを実行
  - cd /d lo_to_ba
    - パスの指定は自分の環境次第
  - conda create -y -n lo_to_ba_py39 -c conda-forge python=3.9 --file requirements.txt
    - Anaconda Promptへのペーストは「Shift + insert」
  - conda activate lo_to_ba_py39  
  - pip install chromedriver-binary==103.0.5060.53.0  
    - PCにインストールされているgoogle chromeのバージョンと合わせる必要あり

## 実行
### 実行1.参加しているプライベートグループリストを作成
- ログインタイプに従って以下のどれかを実行する
  - python bin\lobi\create_private_group_list.py --login_by twitter
    - 20秒弱かかる
  - python bin\lobi\create_private_group_list.py --login_by lobi
  - python bin\lobi\create_private_group_list.py --login_by lobi_unhidden
- 「ログイン失敗」と出た場合
  - 上記コマンドを正しくやり直す
  - パスワードのコピーペーストで失敗している可能性あるので直打ちもしてみる
- 「全て完了」と出た場合
  - 以下2つのファイルができている
    - lo_to_ba/output/joining_private_groups.csv
    - lo_to_ba/output/joining_private_groups.json

### 実行2.保存したいグループの編集
  - lo_to_ba/output/joining_private_groups.csvを右クリック編集して保存したいグループのみに絞る

### 実行3.グループのチャット等を保存*時間かかる
- ログインタイプに従って以下のどれかを実行する
  - python bin\lobi\save_private_group_chats.py --login_by twitter
  - python bin\lobi\save_private_group_chats.py --login_by lobi
  - python bin\lobi\save_private_group_chats.py --login_by lobi_unhidden
- 「ログイン失敗」と出た場合
  - 上記コマンドを正しくやり直す
- 「全て完了」と出た場合
  - lo_to_ba/output/[グループ名]以下に色々バックアップが取れている

## 復元方法
- まだ
- 近いうちに

## 補足
### 並列で実行してはいけない
### ログ
lo_to_ba/log/log  
コマンド実行する度にリセットされるため注意  
エラーが発生した場合は先にlogのコピーを取って新しいコマンドを実行するなど

### Anaconda Promptを開き直したとき
- 環境は既にあるのでAnaconda Promptを開き、以下コマンドのみを実行
  - cd /d lo_to_ba
    - パスの指定は自分の環境次第
  - conda activate lo_to_ba_py39  

### 途中から再開したい場合
lo_to_ba/output/joining_private_groups.csvをメモ帳などで編集し、既に保存が完了しているグループの行を削除

### 途中で止めたい場合
Anaconda Promptで「Ctrl + c」

### 意味不明のエラーが出た場合
requestsのretry機能実装してないせいかも。もう一回やればうまくいくかも。
