public class Main {
    public static void main(String[] args) {
        int[] scores = {80, 60, 90};
        int sum = 0;
        for (int i = 0; i < scores.length; i++) {
            sum += scores[i];
        }
        System.out.println("件数: " + scores.length);
        System.out.println("合計: " + sum);
    }

}
