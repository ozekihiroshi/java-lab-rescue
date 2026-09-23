# 小容量AWSホストでのJava Lab準備

目的は、本番と同じHTTPS・LTI構成で試験できる準備をすることです。既存のMoodle・Python Labを動かしたまま、Java学習者コンテナを起動するところまでは進めません。

## 1. 接続先と容量を確認する（読み取り専用）

確認済みのSSH接続先で、このリポジトリの`public/capacity.py`を実行します。ファイルを配置せずに実行する場合:

```sh
ssh <確認済みの接続先> python3 - < public/capacity.py
```

総メモリ・利用可能メモリ・swap・CPU数・ルートディスク空き・Docker使用量を表示します。起動・停止・pull・設定変更は行いません。Linuxの実ホストで実行してください。Dockerへの読み取り権限がない場合も終了コード2となり、確認不足を示します。

現在の公開構成はHub上限1GiB、学習者上限3GiBです。スクリプトは「1GiB + 3GiB × 人数 + 予備0.5GiB」の利用可能メモリを保守的な予算として確認します。実測消費量や性能保証ではありません。1人でも4.5GiBの空きが必要という判定なので、総2GiBのホストは不合格となります。swapを増やして合格扱いにはしません。

このチェックは起動コマンドへ自動連結されていません。不合格なら以下の設定準備に留め、`up`は実行しないでください。CPU負荷、既存Python利用者の増加、イメージ用ディスク容量も別途確認します。

## 2. HTTPS接続情報を取り込む（Docker操作なし）

Moodle側の`register-lab.py`で、Java専用のHTTPS登録情報を出力します。既存登録の確認なら`--apply`は付けません。新しい登録が必要な場合だけ付けます。実際のMoodleコンテナ名を指定します。

```sh
python3 scripts/register-lab.py --container <Moodleコンテナ名> --lab java \
  --url https://java.school.test --name "Java Lab" \
  --output build/lab-connections/java-public.json
```

Java Lab側で実行:

```sh
python3 public/prepare.py <java-public.json>
```

`public/.env.production`を作成し、ホスト名・Moodle origin・Client ID・deployment IDだけを反映します。新規設定の人数は1です。実環境の値を捏造しません。既存の別接続への上書きは拒否します。既存イメージ・人数などは保持し、最初の取り込み前に`.env.production.before-connect`へ退避します。設定とバックアップはGit管理外です。

この処理では、LTI登録の作成、DNS変更、TLS証明書取得、Dockerネットワーク作成、イメージ取得、サービス起動をしません。Python Labの設定・登録・ボリュームには触れません。ローカル用の`scripts/setup.py connect`とは別の明示的なHTTPS用入口です。

## 3. 起動前に残す準備

- `java.school.test`のDNS、既存Traefikのネットワーク名・証明書resolverを確認し、設定を合わせる。
- Hubと学習者のイメージを容量のある別環境でビルド・発行し、AWSのCPUアーキテクチャに対応するdigestを設定する。AWS上で重いビルドを行わない。イメージ取得前にディスク空きを確認する。
- 設定と既存サービスの保存領域をバックアップし、戻す手順を確認する。新しいJava領域は既存Python領域と分ける。
- メモリ増強後など、容量判定が通ってから`public/verify.py`を実施する。この検査は一時的な最大512MiBのコンテナを動かすため、2GiBホストでは実施を保留する。

実際の起動、HTTPS/LTI受入試験、保存・復元の確認は[公開用手順](README.md)に従います。最初は1人のみです。Hub停止だけでは学習者コンテナが止まらないため、停止時は`python3 scripts/lab.py --public stop`を使います。`down -v`は実行しません。

## 検証状況

HTTPS情報の検証、別接続拒否、繰り返し取り込み、既存設定保持、2GiBでの容量不合格を自動テストします。実際のホストの容量・配置情報は公開資料に含めず、運用者の非公開記録に保管します。JavaのHTTPS・受講者起動は別途検証します。
