package edu.course;
public class Main {
    public static void main(String[] args) {
        StudentService service = new StudentService();
        service.add(new Student("S1", "山田花子", 80));
        service.add(new Student("S2", "佐藤太郎", 59));
        service.updateScore("S2", 59);
        int completed = 0;
        for (Student student : service.all()) {
            if (student.completed()) { completed++; }
        }
        System.out.println("修了者数: " + completed);
    }
}
