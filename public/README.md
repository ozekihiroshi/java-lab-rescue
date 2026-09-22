# Java Lab：HTTPS限定公開用構成

ローカル試作とは独立した、登録受講者向けの公開構成です。既存のTraefik RescueにHTTPSを担当させます。現時点では構成とローカル設定検証までを整備しています。Java用構成のAWSへの配備・DNS変更・外部公開は行っていません。

公開先（ユーザー指定）:

| サービス | URL |
|---|---|
| Moodle | https://moodle.ceri.link |
| Python Lab | https://python-lab.ceri.link |
| Java Lab | https://java-lab.ceri.link |

上記は将来の公開先です。独立リポジトリでは`.env.production.example`から明示的に設定を作成します。Java専用LTI登録のclient ID・deployment IDと、公開イメージdigestは未確定です。Python Labの設定は変更しません。

2026-09-22の接続確認では3ホストともIPv4 `3.114.55.240`へ名前解決しました。JavaホストはWSLからのHTTPS接続で自己署名証明書の検証エラーとなりました。公開前にTraefikのJava用ルート・正規証明書を確認する必要があります。検証を無効にしてLTI接続する運用にはしません。

## 接続と保存の境界

```text
ブラウザ → HTTPS:443 → Traefik → Java Hub:8000 → 受講者コンテナのIDE
                         Moodleの署名済みLTI起動を検証
Java Hub → HTTPS → Moodleの公開鍵エンドポイント
```

- Moodleと別のLabドメインを使います。新規に公開するポートはありません。既存Traefikが80/443を担当し、WebSocketも転送します。8087はローカル試作専用です。
- Compose名は`java-lab-public`。HubのDB・cookie鍵は`java-lab-public_hub_data`、学習者は`java-lab-public-user-*`に保存します。ローカル試作の保存先は移動・共有しません。
- ローカル専用JWKSプロキシは使わず、Moodleの公開HTTPSから鍵を取得します。証明書検証を無効にしません。
- 単一Moodleの`sub`で受講者を識別します。Moodleを変更・再構築して利用者IDを再利用する場合は、既存領域へ接続しないでください。
- 署名・issuer・client ID等のLTI検証に加え、deployment IDとLearner/Instructor/TeachingAssistantロールを確認します。ゲストや別登録からの起動は拒否します。Moodle側でも対象コースを登録受講者に制限してください。
- 1人3GiB・1CPU・256プロセス、同時起動処理1件。総実行人数は必須設定です。上限の例「2人」は収容人数を保証するものではありません。ブラウザを閉じるだけでは停止せず、Hubからログアウトした場合は停止します。
- 学習者は内部ネットワークのみ。外部Maven依存の取得はできないので、必要な依存は学習者イメージへ含めます。CPU・メモリ上限はディスク容量制限にはなりません。ホストの容量監視・利用期限を設けます。

DockerソケットはHubだけに渡しますが、Hub管理権限はホストに強い権限を持ちます。任意コード実行のため、公開Labには専用ホストを推奨します。本構成は信頼関係のある登録受講者向けです。単一ドメイン・共有カーネル・共有内部ネットワークを、不特定多数に対する強固な隔離とみなさないでください。

## 配備前の準備

Linux Docker Engine上で、MoodleとTraefikがHTTPSで動作し、LabのDNSがTraefikを指す状態を用意します。Traefik Rescueの`rescue_proxy`ネットワーク、`websecure`入口と証明書resolverを使用します。異なる構成なら設定を合わせます。

このディレクトリで実行:

```sh
cp .env.production.example .env.production
chmod 600 .env.production
```

ドメイン、Moodle origin（末尾スラッシュなし）、client ID、deployment ID、検証済み同時人数を設定します。Moodleをサブディレクトリ配下に配置する形は現在のテンプレートでは対象外です。`.env.production`はGit管理対象外です。

Hubと学習者のイメージは、既存の`../hub/Dockerfile`と`../singleuser/Dockerfile`をJava Labディレクトリをcontextとしてビルドし、使用するレジストリへ発行します。公開先で両方をpullし、`docker image inspect`の`RepoDigests`を設定へ記録します。ローカル試作タグの上書きは避けてください。設定検証・起動時に暗黙のビルドはしません。現状のDockerfileには取得時に変化し得るOS/Python依存があるため、公開する完成イメージのdigestを固定します。digest固定は脆弱性検査の代わりではありません。

MoodleでJava専用のLTI 1.3外部ツールを登録します。

| 項目 | 値（ドメインは置換） |
|---|---|
| ツールURL | `https://java.school.tld/hub/user-redirect/ide/` |
| ログイン開始URL | `https://java.school.tld/hub/lti13/oauth_login` |
| リダイレクトURI | `https://java.school.tld/hub/lti13/oauth_callback` |
| 公開鍵 | この構成はMoodleへのサービス呼出し・成績返却を使用しません。ツール鍵は生成しません |
| 起動表示 | 新しいウィンドウ（iframe埋め込みを前提にしない） |

Moodle登録が示すclient IDとdeployment IDを設定します。公開教材のLabリンクはこの登録を使い、単元ごとの`/hub/user-redirect/ide/?folder=...`を設定します。既存のローカル登録・コース55/56は書き換えません。提出はファイルを取得してMoodle標準課題へアップロードする方式です。

## 検証・初回起動・日常操作

```sh
# Compose構成と、ローカルに取得済みの固定版Hubイメージを検証。
# 一時コンテナはネットワーク・Dockerソケット・実データを持ちません。
python3 verify.py

# 検証後、実際の公開先ホストで初回配備するときだけ実行。
docker compose --env-file .env.production -f compose.yml up -d --no-build --pull never
```

日常操作はリポジトリのルートから同じ共通入口を使えます。接続先Docker Engineを事前に確認してください。

```sh
python3 scripts/lab.py --public status
python3 scripts/lab.py --public logs --tail 50
python3 scripts/lab.py --public stop
python3 scripts/lab.py --public start
```

停止は学習者コンテナ→Hubの順で、保存ボリュームを削除しません。通常の`docker compose stop`だけでは、Hubが生成した学習者コンテナは停止しません。公開環境は`authoring --labs both`の対象には含めません。

設定・イメージ更新は再検証後に明示的な`up -d --no-build --pull never`で反映します。既存の学習者コンテナには旧イメージが残るため、保存を周知して全員を停止してから更新し、再起動を確認します。データ削除の`down -v`は使いません。

## 公開前の受入確認（実ドメインで未実施）

1. HTTPS証明書とHTTP→HTTPS誘導、外部から8000/8081/8087が開いていないこと。
2. Moodleから受講者2人と教師が起動でき、ゲスト・別deployment・認証なしのIDEアクセスが拒否されること。
3. 正しい単元を開き、Java編集・型診断・コンパイル・実行・端末停止・ダウンロード・課題提出・教師取得ができること。WebSocketも確認。
4. 学習者間で内容が混ざらず、停止・再開・コンテナ再作成後にファイルが保持されること。
5. 同時人数上限で追加起動が拒否されること、ホストに余裕があること、メモリ不足から回復できること。
6. 次のバックアップ・復元を別環境で実施し、本人対応と提出内容を確認すること。

## バックアップと復元

メンテナンス時間に保存を依頼し、共通入口で`java-public stop`を実行します。`status`とDocker一覧で学習者も停止したことを確認してから、Hubボリュームと**全ての**`java-lab-public-user-*`ボリュームを、所有者・権限を維持してホストのバックアップ手順で取得します。学習者領域はComposeのvolume一覧に含まれないため、取り漏らさないでください。

設定ファイル・公開イメージdigest・Moodle側LTI登録との対応・バックアップ時点のMoodle利用者対応も保管します。cookie鍵や個人ファイルを含むため、暗号化とアクセス制限を適用します。稼働中のSQLiteファイルだけをコピーしません。

復元試験は隔離した別ホストで同じイメージ・設定・ボリューム所有者を戻します。Moodleの利用者IDとの対応を先に確認し、別人の領域を開かないことを検証してから再開します。MoodleコースのバックアップだけではLabの未提出ファイルは復元できません。

## 検証根拠

WSLでこのディレクトリから`python3 test_local.py`を実行すると、既存のローカルHubイメージを使って設定試験を再実行できます（既定は独立リポジトリのHubイメージ、別イメージは`--hub-image`）。一時コンテナにDockerソケット・永続データ・外部通信は渡しません。公開環境の完成イメージに対する検査は`verify.py`です。

ローカルで公開Composeの解決、HTTPポート非公開・内部ネットワーク・digest必須の検査、設定の異常値拒否、deployment/ロールの許可・拒否を検証しました。既存Hub 5.5.0 / LTIAuthenticator 1.6.3 / DockerSpawner 14.0.0の一時コンテナで設定をロードしました。実ドメインのTLS/LTI、レジストリ配布、同時負荷、復元は未検証です。

仕様参照: [LTI設定](https://ltiauthenticator.readthedocs.io/en/latest/lti13/getting-started.html)、[LTI設定リファレンス](https://ltiauthenticator.readthedocs.io/en/latest/lti13/reference.html)、[JupyterHubの同時実行上限](https://jupyterhub.readthedocs.io/en/latest/reference/api/app.html)。
