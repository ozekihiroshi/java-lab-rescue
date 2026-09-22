# Java Lab Rescue

ブラウザでJavaを編集・実行する、Moodle LTI 1.3連携のDocker環境です。
JupyterHubが受講者別のコンテナを起動し、code-server、Temurin JDK 21、Java拡張、Mavenを提供します。
Docker Engine + Composeを使用します。WindowsではWSL内のEngineで動作し、Docker Desktopは不要です。

## このリポジトリの範囲

- Dockerイメージ、ローカル構成、将来のHTTPS限定公開用構成。
- 初期JavaファイルとオフラインMaven依存、検証ツール。
- Moodle本体・コース作成・教師用解答・提出物は含みません。教材編集は[moodle-rescue](https://github.com/ozekihiroshi/moodle-rescue)側です。

## 最初に選ぶ使い方

| 用途 | 操作 | 接続/保存領域 |
|---|---|---|
| Moodleなしの単独検証 | `--standalone` | localhost:8088、専用ユーザー/専用ボリューム |
| Moodleの授業から利用 | 通常モード | localhost:8087、Moodleの受講者別領域 |
| 将来のHTTPS限定公開 | `--public` | 別Compose。単独検証のパスワード認証は使用しない |

単独検証だけならMoodleもLTI登録も不要です。

```sh
python3 scripts/setup.py standalone
python3 scripts/lab.py --standalone build
python3 scripts/lab.py --standalone up
```

`http://127.0.0.1:8088`を開き、ユーザー名`learner`、生成された`.env.standalone`内のパスワードでログインします。停止は`python3 scripts/lab.py --standalone stop`です。localhost限定の検証用で、インターネットには公開しません。繰り返しsetupしても既存パスワードは変えません。

単独検証の作業はMoodle受講者の作業と自動的に混ぜません。初回接続の手順は[連携ガイド](docs/connection.md)を参照してください。

## Moodle連携モードの初回構築

Linux/WSLでDocker EngineとComposeを用意し、Moodleを先に起動します。標準設定ではローカルMoodle `http://localhost:8083` と外部Dockerネットワーク `moodle-rescue-local_local_access` を使います。別のMoodleなら`.env`のURL・ネットワーク名を変更します。

```sh
git clone git@github.com:ozekihiroshi/java-lab-rescue.git
cd java-lab-rescue
cp .env.example .env
```

Moodleの「外部ツール」でLTI 1.3登録を作り、`.env`の`LTI_CLIENT_ID`にその値を設定します。登録するURL:

| 項目 | ローカルの値 |
|---|---|
| ツールURL | `http://localhost:8087/hub/user-redirect/ide/` |
| ログイン開始URL | `http://localhost:8087/hub/lti13/oauth_login` |
| リダイレクトURI | `http://localhost:8087/hub/lti13/oauth_callback` |

氏名やメールをユーザーキーにせず、Moodleの`sub`を使います。起動は新しいウィンドウにし、ゲストの実習利用は許可しません。単元URLの例は `/hub/user-redirect/ide/?folder=/home/jovyan/work/java-intro/course-v2/lesson-1-1` です。

```sh
python3 scripts/lab.py build
python3 scripts/lab.py up
python3 scripts/lab.py status
```

ブラウザではMoodleのLab活動から入ります。LabのURLを直接開いてもMoodle認証の代わりにはなりません。提出はIDEから取得し、Moodleの標準課題へアップロードします。

## 日常操作

```sh
python3 scripts/lab.py start
python3 scripts/lab.py status
python3 scripts/lab.py logs --tail 30
python3 scripts/lab.py stop
```

`up`は初回作成・設定変更反映、`start`は既存コンテナ再開です。`stop`は学習者→Hubの順に止め、ボリュームを削除しません。Hubが作る学習者コンテナはComposeだけの停止では残るため、この入口を使います。終了前にファイルを保存してください。保存先は学習者別`JAVA_USER_VOLUME_PREFIX-*`、Hub DBはプロジェクトの`hub_data`です。

1人3GiB/1CPU、言語サーバーのヒープは1GiBです。OS、Moodle、Hubの余裕も必要です。学習者ネットワークは内部専用で、Mavenは組み込み済みの依存をオフライン利用します。Moodleバックアップに未提出のLabファイルは含まれません。

## 既存試作から移行する場合

[移行手順](docs/migration.md)に従い、既存のLTI client ID、Composeプロジェクト名、ネットワーク名、学習者名・ボリュームの接頭辞を保持します。名前を変えると別の空環境になります。既存のMoodleコースや提出物を作り直す必要はありません。

## 検証と公開用構成

`python3 checks/local.py`は構成とHub正常性を確認します。`checks/image.py`は一時学習者コンテナ用の教材/Maven検査です。公開用設定の試験は `python3 public/test_local.py --hub-image java-lab-rescue-hub:local` です。

[公開用構成](public/README.md)は将来の限定公開向けです。今回の作業対象はGitHubで管理する独立環境とローカル検証であり、AWS配備は行いません。

## ライセンス

このリポジトリに移したソフトウェア・Javaコードは元のmoodle-rescueのGPL-3.0-or-laterを継承します（[LICENSE](LICENSE)）。依存ソフトウェアは各ライセンスに従います。Dockerイメージ配布時も依存物の通知とライセンス条件を維持してください。

今回の実施結果と未検証範囲は[検証記録](docs/verification.md)を参照してください。

GitHubからcloneしたイメージの初期教材・オフラインMaven検査は、リポジトリ直下で次のように再実行できます（検査用コンテナは終了時に削除し、既存の受講者ボリュームには接続しません）。

```sh
docker run --rm --network none --memory 1g --cpus 1 \
  -v "$PWD/checks/image.py:/check.py:ro" --entrypoint python \
  java-lab-rescue-singleuser:local /check.py
```
