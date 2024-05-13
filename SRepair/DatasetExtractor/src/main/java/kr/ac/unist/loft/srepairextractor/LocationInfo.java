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
    public LocationInfo(String buggyFunc, String buggyFuncWithFL, MethodSignature methodSignature, JsonObject tests,
                        String javadocString) {
        this.buggyFunc = buggyFunc.trim();
        this.buggyFuncWithFL = buggyFuncWithFL.trim();
        this.methodSignature = methodSignature;
        this.tests = tests;
        this.javadocString = javadocString.trim();
    }

    public JsonObject toJson() {
        JsonObject obj = new JsonObject();
        obj.addProperty("buggy", buggyFunc);
        obj.addProperty("buggy_fl", buggyFuncWithFL);
        obj.add("method_signature", methodSignature.toJson());
        obj.add("trigger_test", tests);
        obj.addProperty("buggy_code_comment", javadocString);
        return obj;
    }
}
