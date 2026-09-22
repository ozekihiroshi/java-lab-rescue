import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        while (scanner.hasNextLine()) {
            String line = scanner.nextLine();
            try {
                int score = Integer.parseInt(line);
                if (score < 0 || score > 100) {
                    System.out.println("範囲外");
                } else {
                    System.out.println("得点: " + score);
                    break;
                }
            } catch (NumberFormatException error) {
                System.out.println("整数を入力してください");
            }
        }
    }

}
