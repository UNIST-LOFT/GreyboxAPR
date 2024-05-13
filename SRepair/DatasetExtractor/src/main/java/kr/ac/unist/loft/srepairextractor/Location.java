package kr.ac.unist.loft.srepairextractor;

public class Location {
    String file;
    int line;
    float score;
    public Location(String file, int line, float score) {
        this.file = file;
        this.line = line;
        this.score = score;
    }
}
