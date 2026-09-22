import java.util.Map;
import java.util.HashMap;
public class Main {
    public static void main(String[] args) {
        Map<String, Student> students = new HashMap<>();
        students.put("S001", new Student("山田花子", 80));
        String id = "S001";
        if (students.containsKey(id)) {
            System.out.println("重複ID: " + id);
        } else {
            students.put(id, new Student("佐藤太郎", 60));
        }
        System.out.println("件数: " + students.size());
    }
}
