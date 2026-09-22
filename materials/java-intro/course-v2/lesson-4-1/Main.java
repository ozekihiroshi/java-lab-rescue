public class Main {
    public static void main(String[] args) {
        Student first = new Student();
        first.name = "山田花子";
        first.score = 80;
        Student second = first;
        second.score = 90;
        System.out.println(first.name + ": " + first.score);
    }
}
