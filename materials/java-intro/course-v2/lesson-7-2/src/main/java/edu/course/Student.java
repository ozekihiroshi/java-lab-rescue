package edu.course;
public class Student {
    private final String id;
    private final String name;
    private final int score;
    public Student(String id, String name, int score) {
        if (id == null || id.isBlank() || name == null || name.isBlank()) {
            throw new IllegalArgumentException("IDと名前は空欄にできません");
        }
        if (score < 0 || score > 100) {
            throw new IllegalArgumentException("得点は0〜100");
        }
        this.id = id;
        this.name = name;
        this.score = score;
    }
    public String getId() { return id; }
    public String getName() { return name; }
    public int getScore() { return score; }
    public boolean completed() { return score >= 60; }
}
