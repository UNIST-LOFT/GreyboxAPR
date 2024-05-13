package kr.ac.unist.loft.srepairextractor;

import com.google.gson.JsonObject;

public class LocationInfo {
    static class MethodSignature {
        public String returnType;
        public String methodName;
        public String params;
        public MethodSignature(String returnType, String methodName, String params) {
            this.returnType = returnType;
            this.methodName = methodName;
            this.params = params;
        }

        public JsonObject toJson() {
            JsonObject obj = new JsonObject();
            obj.addProperty("return_type", returnType);
            obj.addProperty("method_name", methodName);
            obj.addProperty("params_string", params);
            return obj;
        }
    }

    private String buggyFunc;
    private String buggyFuncWithFL;
    private MethodSignature methodSignature;
    private JsonObject tests;
    private String javadocString;

    private int startLine;
    private int endLine;
    private String filePath;

    private Location location;
    public LocationInfo(String buggyFunc, String buggyFuncWithFL, MethodSignature methodSignature, JsonObject tests,
                        String javadocString, int startLine, int endLine, String filePath, Location location) {
        this.buggyFunc = buggyFunc.trim();
        this.buggyFuncWithFL = buggyFuncWithFL.trim();
        this.methodSignature = methodSignature;
        this.tests = tests;
        this.javadocString = javadocString.trim();
        this.startLine = startLine;
        this.endLine = endLine;
        this.filePath = filePath;
        this.location = location;
    }

    public JsonObject toJson() {
        JsonObject obj = new JsonObject();
        obj.addProperty("buggy", buggyFunc);
        obj.addProperty("buggy_fl", buggyFuncWithFL);
        obj.add("method_signature", methodSignature.toJson());
        obj.add("trigger_test", tests);
        obj.addProperty("buggy_code_comment", javadocString);
        obj.addProperty("start_line", startLine);
        obj.addProperty("end_line", endLine);
        obj.addProperty("file_path", filePath);
        obj.add("location", location.toJson());
        return obj;
    }
}
