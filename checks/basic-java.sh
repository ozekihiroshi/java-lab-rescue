#!/bin/sh
set -eu
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cp /materials/Main.java "$work/Main.java"
cd "$work"
java -version
javac -encoding UTF-8 Main.java
java Main > result.txt
printf '受講者: 山田花子\n得点: 80\n' > expected.txt
cmp result.txt expected.txt
sed -i 's/int score = 80;/int score = "80";/' Main.java
if javac -encoding UTF-8 Main.java > error.txt 2>&1; then
    echo 'Expected type error was not detected' >&2
    exit 1
fi
sed -i 's/int score = "80";/int score = 90;/' Main.java
javac -encoding UTF-8 Main.java
java Main > result.txt
printf '受講者: 山田花子\n得点: 90\n' > expected.txt
cmp result.txt expected.txt
cat result.txt
printf 'PASS: Japanese output, intentional type error, repair and recompile\n'
