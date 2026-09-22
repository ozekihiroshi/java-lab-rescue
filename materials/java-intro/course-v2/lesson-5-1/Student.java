public class Student {
    private final String name;
    private int score;
    public Student(String name, int score) {
        this.name = name;
        setScore(score);
    }
    public String getName() { return name; }
    public int getScore() { return score; }
    public void setScore(int score) {
        if (score < 0 || score > 100) {
            throw new IllegalArgumentException("得点は0〜100");
        }
        this.score = score;
    }
    public boolean completed() { return score >= 60; }
}
