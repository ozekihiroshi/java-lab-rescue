public class Main {
    public static void main(String[] args) {
        Student student = new Student("山田花子", 59);
        System.out.println(student.getName() + ": " + student.completed());
    }
}
