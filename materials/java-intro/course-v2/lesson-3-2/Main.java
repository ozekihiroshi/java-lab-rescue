public class Main {
    public static void main(String[] args) {
        int[] scores = {80, 60, 90};
        System.out.println("合計: " + total(scores));
    }
    static int total(int[] values) {
        int sum = 0;
        for (int value : values) {
            sum += value;
        }
        return sum;
    }

}
