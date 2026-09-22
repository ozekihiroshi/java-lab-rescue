package edu.course;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVRecord;

public class CsvStore {
    public List<Student> load(Path path) throws IOException {
        List<Student> result = new ArrayList<>();
        if (!Files.exists(path)) { return result; }
        Set<String> ids = new HashSet<>();
        try (var reader = Files.newBufferedReader(path, StandardCharsets.UTF_8);
             var parser = CSVFormat.DEFAULT.parse(reader)) {
            var rows = parser.iterator();
            if (!rows.hasNext()) { throw new IOException("ヘッダーがありません"); }
            CSVRecord header = rows.next();
            if (header.size() != 3 || !header.get(0).equals("student_id")
                    || !header.get(1).equals("name") || !header.get(2).equals("score")) {
                throw new IOException("CSVヘッダーが違います");
            }
            while (rows.hasNext()) {
                CSVRecord row = rows.next();
                if (row.size() != 3) { throw new IOException("列数が違います: " + row.getRecordNumber()); }
                try {
                    Student student = new Student(row.get(0), row.get(1), Integer.parseInt(row.get(2)));
                    if (!ids.add(student.getId())) {
                        throw new IllegalArgumentException("重複ID");
                    }
                    result.add(student);
                } catch (IllegalArgumentException error) {
                    throw new IOException("不正なCSVレコード: " + row.getRecordNumber(), error);
                }
            }
        }
        return result;
    }
    public void save(Path path, List<Student> students) throws IOException {
        Path destination = path.toAbsolutePath();
        Path temp = Files.createTempFile(destination.getParent(), ".students-", ".csv");
        try {
            try (var writer = Files.newBufferedWriter(temp, StandardCharsets.UTF_8);
                 var printer = CSVFormat.DEFAULT.print(writer)) {
                printer.printRecord("student_id", "name", "score");
                for (Student student : students) {
                    printer.printRecord(student.getId(), student.getName(), student.getScore());
                }
            }
            try {
                Files.move(temp, destination, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
            } catch (AtomicMoveNotSupportedException error) {
                Files.move(temp, destination, StandardCopyOption.REPLACE_EXISTING);
            }
        } finally {
            Files.deleteIfExists(temp);
        }
    }
}
