package edu.course;
public class Main {
    public static void main(String[] args) {
        Student student = new Student("山田花子", 80);
        System.out.println(student.getName() + ": " + student.getScore());
    }
}
