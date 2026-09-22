import java.util.List;
public class Main {
    public static void main(String[] args) {
        List<Student> students = List.of(new Student("山田花子", 80), new Student("佐藤太郎", 60));
        String target = "佐藤太郎";
        boolean found = false;
        for (Student student : students) {
            if (student.getName().equals(target)) {
                student.setScore(90);
                System.out.println(student.getName() + ": " + student.getScore());
                found = true;
                break;
            }
        }
        if (!found) {
            System.out.println("見つかりません");
        }
    }
}
