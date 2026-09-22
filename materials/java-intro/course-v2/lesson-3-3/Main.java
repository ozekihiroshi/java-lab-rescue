public class Main {
    public static void main(String[] args) {
        int[] scores = {80, 81};
        if (scores.length == 0) {
            System.out.println("データなし");
        } else {
            System.out.println("平均: " + average(scores));
        }
    }
    static double average(int[] values) {
        int sum = 0;
        for (int value : values) {
            sum += value;
        }
        return (double) sum / values.length;
    }

}
