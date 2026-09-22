package edu.course;
import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.io.*;
import java.util.List;

class ProjectTest {
    @TempDir Path temp;
    @Test void boundariesAndRequiredFields() {
        assertFalse(new Student("S1", "花子", 59).completed());
        assertTrue(new Student("S1", "花子", 60).completed());
        assertEquals(0, new Student("S1", "花子", 0).getScore());
        assertEquals(100, new Student("S1", "花子", 100).getScore());
        assertThrows(IllegalArgumentException.class, () -> new Student("S1","花子",-1));
        assertThrows(IllegalArgumentException.class, () -> new Student("S1","花子",101));
        assertThrows(IllegalArgumentException.class, () -> new Student("","花子",80));
        assertThrows(IllegalArgumentException.class, () -> new Student("S1"," ",80));
    }
    @Test void duplicateAndMissingIdDoNotChangeState() {
        StudentService service = new StudentService();
        service.add(new Student("S1", "花子", 80));
        assertThrows(IllegalArgumentException.class, () -> service.add(new Student("S1", "太郎", 60)));
        assertThrows(IllegalArgumentException.class, () -> service.updateScore("missing", 50));
        assertThrows(IllegalArgumentException.class, () -> service.updateScore("S1", 101));
        assertEquals(1, service.all().size());
        assertEquals(80, service.all().get(0).getScore());
        service.updateScore("S1", 60);
        assertEquals(60, service.all().get(0).getScore());
    }
    @Test void csvRoundTripSpecialCharactersAndEmptyData() throws Exception {
        CsvStore store = new CsvStore();
        Path path = temp.resolve("受講者.csv");
        String name = "山田,\"花子\"\n研修生";
        store.save(path, List.of(new Student("S1", name, 80)));
        List<Student> restored = store.load(path);
        assertEquals(1, restored.size());
        assertEquals(name, restored.get(0).getName());
        assertEquals(80, restored.get(0).getScore());
        store.save(path, List.of());
        assertTrue(store.load(path).isEmpty());
    }
    @Test void rejectsMalformedCsv() throws Exception {
        CsvStore store = new CsvStore();
        Path path = temp.resolve("bad.csv");
        for (String content : List.of("", "id,name,score\n", "student_id,name,score\nS1,花子\n",
                "student_id,name,score\nS1,花子,abc\n", "student_id,name,score\nS1,花子,101\n",
                "student_id,name,score\nS1,花子,80\nS1,太郎,60\n")) {
            Files.writeString(path, content, StandardCharsets.UTF_8);
            assertThrows(IOException.class, () -> store.load(path));
        }
    }
    @Test void cliPersistsAndRejectsInvalidInputWithoutChangingFile() throws Exception {
        Path path = temp.resolve("students.csv");
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        PrintStream out = new PrintStream(bytes, true, StandardCharsets.UTF_8);
        assertEquals(0, Main.run(new String[]{path.toString(),"add","S1","花子","80"},out));
        byte[] original = Files.readAllBytes(path);
        assertEquals(1, Main.run(new String[]{path.toString(),"add","S1","太郎","60"},out));
        assertEquals(1, Main.run(new String[]{path.toString(),"update","S1","abc"},out));
        assertArrayEquals(original, Files.readAllBytes(path));
        assertEquals(1, Main.run(new String[]{path.toString(),"update","S1","60"},out));
        bytes.reset();
        assertEquals(0, Main.run(new String[]{path.toString(),"list"},out));
        assertTrue(bytes.toString(StandardCharsets.UTF_8).contains("S1: 花子: 80: 修了"));
        Files.writeString(path,"壊れたヘッダー\n",StandardCharsets.UTF_8);
        byte[] broken = Files.readAllBytes(path);
        assertEquals(1, Main.run(new String[]{path.toString(),"add","S2","次郎","90"},out));
        assertArrayEquals(broken,Files.readAllBytes(path));
    }
}
