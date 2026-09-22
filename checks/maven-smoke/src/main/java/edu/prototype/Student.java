package edu.prototype;
public record Student(String name, int score) {
    public Student {
        if (score < 0 || score > 100) throw new IllegalArgumentException("score");
    }
    public boolean completed() { return score >= 60; }
}
