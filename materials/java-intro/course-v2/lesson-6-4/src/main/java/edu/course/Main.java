package edu.course;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.io.IOException;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVRecord;

public class Main {
    public static void main(String[] args) throws IOException {
        String name = "山田花子";
        Path path = Path.of("students.csv");
        try (var writer = Files.newBufferedWriter(path, StandardCharsets.UTF_8);
             var printer = CSVFormat.DEFAULT.print(writer)) {
            printer.printRecord("student_id", "name", "score");
            printer.printRecord("S001", name, 80);
        }
        try (var reader = Files.newBufferedReader(path, StandardCharsets.UTF_8);
             var parser = CSVFormat.DEFAULT.builder()
                 .setHeader("student_id", "name", "score").setSkipHeaderRecord(true).get().parse(reader)) {
            var rows = parser.getRecords();
            CSVRecord row = rows.get(0);
            System.out.println("件数: " + rows.size());
            System.out.println("名前一致: " + name.equals(row.get("name")));
            System.out.println("得点: " + Integer.parseInt(row.get("score")));
        }
    }
}
