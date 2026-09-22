#!/bin/sh
set -eu
cd "$(dirname "$0")"
mvn -B -o -Dmaven.repo.local=/opt/maven-cache test
java -cp "target/classes:/opt/maven-cache/org/apache/commons/commons-csv/1.14.0/commons-csv-1.14.0.jar:/opt/maven-cache/commons-io/commons-io/2.18.0/commons-io-2.18.0.jar:/opt/maven-cache/commons-codec/commons-codec/1.18.0/commons-codec-1.18.0.jar" edu.course.Main "$@"
