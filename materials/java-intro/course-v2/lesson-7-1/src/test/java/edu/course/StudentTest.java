package edu.course;
import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
class StudentTest {
    @Test void boundary() {
        assertFalse(new Student("S1","花子",59).completed());
        assertTrue(new Student("S1","花子",60).completed());
    }
}
