import java.util.List;
import java.util.ArrayList;
public class Main {
    public static void main(String[] args) {
        List<Student> students = new ArrayList<>();
        students.add(new Student("山田花子", 80));
        for (Student student : students) {
            System.out.println(student.getName() + ": " + student.getScore());
        }
        System.out.println("件数: " + students.size());
    }
}
