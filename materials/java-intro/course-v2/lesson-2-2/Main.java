public class Main {
    public static void main(String[] args) {
        int score = 101;
        boolean present = true;
        if (score < 0 || score > 100) {
            System.out.println("得点が範囲外");
        } else if (score >= 60 && present) {
            System.out.println("修了");
        } else {
            System.out.println("再学習");
        }
    }

}
