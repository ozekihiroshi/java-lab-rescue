package edu.prototype;
import static org.junit.jupiter.api.Assertions.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.charset.StandardCharsets;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.apache.commons.csv.CSVFormat;

class StudentTest {
    @TempDir Path temp;
    @Test void boundaries() {
        assertFalse(new Student("花子", 59).completed());
        assertTrue(new Student("花子", 60).completed());
        assertTrue(new Student("花子", 100).completed());
        assertThrows(IllegalArgumentException.class, () -> new Student("花子", -1));
        assertThrows(IllegalArgumentException.class, () -> new Student("花子", 101));
    }
    @Test void csvRoundTrip() throws Exception {
        String name = "山田,\"花子\"\n受講者";
        Path path = temp.resolve("受講者.csv");
        try (var writer = Files.newBufferedWriter(path, StandardCharsets.UTF_8);
             var csv = CSVFormat.DEFAULT.print(writer)) {
            csv.printRecord(name, 80);
        }
        try (var reader = Files.newBufferedReader(path, StandardCharsets.UTF_8);
             var csv = CSVFormat.DEFAULT.parse(reader)) {
            var rows = csv.getRecords();
            assertEquals(1, rows.size());
            assertEquals(name, rows.get(0).get(0));
            assertEquals(80, Integer.parseInt(rows.get(0).get(1)));
        }
    }
}
