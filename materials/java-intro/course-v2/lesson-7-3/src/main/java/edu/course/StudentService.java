package edu.course;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class StudentService {
    private final Map<String, Student> students = new LinkedHashMap<>();
    public void add(Student student) {
        if (students.containsKey(student.getId())) {
            throw new IllegalArgumentException("重複ID: " + student.getId());
        }
        students.put(student.getId(), student);
    }
    public void updateScore(String id, int score) {
        Student previous = students.get(id);
        if (previous == null) {
            throw new IllegalArgumentException("未登録ID: " + id);
        }
        Student updated = new Student(id, previous.getName(), score);
        students.put(id, updated);
    }
    public List<Student> all() {
        return List.copyOf(students.values());
    }
}
