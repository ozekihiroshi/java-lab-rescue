# moodle-rescue内の試作からの移行

移動するのはソースとDocker操作の入口です。教材コース・提出物・Dockerボリュームは移動や削除をしません。

1. 新リポジトリを旧リポジトリと並べてcloneします。
2. 旧`prototypes/java-lab/.env`のLTI client IDを新`.env`へ設定します。資格情報はcommitしません。
3. 現在の試作を引き継ぐ場合、次の値を設定します。

```dotenv
COMPOSE_PROJECT_NAME=java-lab-prototype
JAVA_CONTAINER_PREFIX=java-lab-prototype
JAVA_LEARNER_NETWORK=java-lab-prototype-learners
JAVA_USER_VOLUME_PREFIX=java-lab-prototype-user
JAVA_HUB_IMAGE=java-lab-rescue-hub:local
JAVA_SINGLEUSER_IMAGE=java-lab-rescue-singleuser:local
```

4. `docker inspect`で既存Hubのprojectラベルと保存ボリューム、受講者の保存先を記録します。設定と一致しなければ止めて確認します。
5. 新ディレクトリで`python3 scripts/lab.py build`を実行します。旧イメージのタグは上書きしません。
6. 受講者に保存を依頼し、`python3 scripts/lab.py stop`で既存実習を停止します。
7. `python3 scripts/lab.py up`でHubと鍵中継を再作成します。同一projectなので同じHubデータを使います。
8. Moodleから既存利用者で起動し、保存ファイル・Java実行・提出を確認します。新受講者の分離も確認します。

ロールバックは新環境を停止し、旧ディレクトリで旧設定の`docker compose up -d --no-build jwks jupyterhub`を使います。保存ボリュームはそのままです。Hub DBのバージョンを変える更新は、別途停止時バックアップと復元試験が必要です。
