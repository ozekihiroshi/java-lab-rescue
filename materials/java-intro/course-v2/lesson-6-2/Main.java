import java.nio.file.Path;
import java.nio.file.Files;
import java.nio.charset.StandardCharsets;
import java.io.IOException;

public class Main {
    public static void main(String[] args) throws IOException {
        Path path = Path.of("report.txt");
        try (var writer = Files.newBufferedWriter(path, StandardCharsets.UTF_8)) {
            writer.write("受講者: 山田花子\n");
        }
        for (String line : Files.readAllLines(path, StandardCharsets.UTF_8)) {
            System.out.println(line);
        }
    }

}
