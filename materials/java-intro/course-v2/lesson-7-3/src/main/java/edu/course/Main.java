package edu.course;
import java.io.IOException;
import java.io.PrintStream;
import java.io.UncheckedIOException;
import java.nio.file.Path;

public class Main {
    public static void main(String[] args) {
        System.exit(run(args, System.out));
    }
    static int run(String[] args, PrintStream out) {
        if (args.length == 0) {
            out.println("使い方: sh run.sh students.csv list|add ID 名前 得点|update ID 得点");
            return 0;
        }
        try {
            if (args.length < 2) { throw new IllegalArgumentException("ファイルと操作を指定してください"); }
            Path path = Path.of(args[0]);
            CsvStore store = new CsvStore();
            StudentService service = new StudentService();
            for (Student student : store.load(path)) { service.add(student); }
            String command = args[1];
            if (command.equals("list") && args.length == 2) {
                for (Student student : service.all()) {
                    out.println(student.getId() + ": " + student.getName() + ": " +
                        student.getScore() + ": " + (student.completed() ? "修了" : "再学習"));
                }
                out.println("件数: " + service.all().size());
            } else if (command.equals("add") && args.length == 5) {
                service.add(new Student(args[2], args[3], Integer.parseInt(args[4])));
                store.save(path, service.all());
                out.println("登録: " + args[2]);
            } else {
                throw new IllegalArgumentException("操作または引数の数が違います");
            }
            return 0;
        } catch (IOException | UncheckedIOException | IllegalArgumentException error) {
            out.println("エラー: " + error.getMessage());
            return 1;
        }
    }
}
