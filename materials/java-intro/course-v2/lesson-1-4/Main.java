import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.println("名前を入力:");
        String name = scanner.nextLine();
        System.out.println("得点を入力:");
        int score = Integer.parseInt(scanner.nextLine());
        System.out.println(name + ": " + score);
    }

}
