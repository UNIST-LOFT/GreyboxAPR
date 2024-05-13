package kr.ac.unist.loft.srepairextractor;

import com.google.gson.JsonObject;

public class Location {
    String file;
    int line;
    float score;
    public Location(String file, int line, float score) {
        this.file = file;
        this.line = line;
        this.score = score;
    }

    public JsonObject toJson() {
        JsonObject obj = new JsonObject();
        obj.addProperty("file", file);
        obj.addProperty("line", line);
        obj.addProperty("score", score);
        return obj;
    }
}
