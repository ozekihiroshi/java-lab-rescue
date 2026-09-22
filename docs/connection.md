# Java LabとMoodleの接続

Labの実行基盤とMoodleの教材/利用者管理を分け、登録情報JSONだけを受け渡します。Labの起動だけでMoodle登録は作られません。単独検証、管理者の初回接続、教師の単元追加は別の作業です。

## 管理者の初回接続

Moodle側の汎用登録アダプターを用意しました。現在はmoodle-rescueの`codex/lab-connection-setup`ブランチにあります（mainへの統合前）。[手順とアダプター](https://github.com/ozekihiroshi/moodle-rescue/blob/codex/lab-connection-setup/docs/lab-connection-setup.md)を参照し、その版のMoodleリポジトリから次を実行します。

```sh
python3 scripts/register-lab.py --lab java --url http://localhost:8087 \
  --name "Java Lab" --output build/lab-connections/java.json --apply
```

この処理は未登録ならツールを作成し、正しい既存登録なら同じClient IDを出力します。コース・受講者・課題は作りません。既存の試作登録を利用する場合は名前を`Java Lab Prototype`に変え、`--apply`なしで出力できます。

Java Lab側で取り込みます。

```sh
python3 scripts/setup.py connect ../moodle-rescue/build/lab-connections/java.json
python3 scripts/lab.py check
python3 scripts/lab.py build
python3 scripts/lab.py up
```

手でClient IDやURLを何か所も転記する必要はありません。既存の接続先が異なる場合は上書きを拒否します。元の保存先設定は保持します。取り込み前の既存設定は`runtime/env-before-connect`へ一度だけ保存します。実行中の環境を更新する場合は保存を周知して先にstopしてください。

この取り込みはローカルHTTP用です。HTTPS公開用は引き続き`public/README.md`の手順を使用します。Moodleが別Dockerネットワーク/別内部ホスト名なら`.env`の`MOODLE_NETWORK`と`MOODLE_INTERNAL_URL`を合わせます。JSONはDockerネットワークを自動作成するものではありません。

## 教師の教材設定

コースの外部ツール活動で登録済みJava Labを選び、単元のフォルダーをURLで指定します。

```text
http://localhost:8087/hub/user-redirect/ide/?folder=/home/jovyan/work/java-intro/course-v2/lesson-1-1
```

学生はMoodleへログインして活動を開くだけです。Labへ別パスワードを設定する必要はありません。ゲスト利用を許可せず、新しいウィンドウで開きます。初期ファイルがイメージ内にあることと、Moodle側の提出課題を用意したことを確認します。

## 試験

`python3 checks/standalone.py`は単独環境のログイン/IDE/Java実行/停止再開後の保持を確認します（単独環境を一度停止）。`python3 checks/test_setup.py`は再取り込みと誤接続拒否を検査します。`checks/local.py`はMoodle連携環境の稼働検査です。署名付きLTIや学生の提出操作は、最後にMoodleから受講者アカウントで通して確認します。

## Python Labと共通の手順

両LabともMoodle側の`register-lab.py`でJSONを出力し、Lab側の`scripts/setup.py connect`で取り込みます。Pythonは`--lab python`・8086・`python.json`、Javaは`--lab java`・8087・`java.json`です。起動コマンドと教材URLは各Labの手順に従います。Python側の取り込みは[専用ブランチの導入案内](https://github.com/ozekihiroshi/python-lab-rescue/blob/codex/lab-connection-import/docs/connection.md)で提供しています（main統合前）。
