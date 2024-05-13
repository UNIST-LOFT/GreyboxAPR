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
        this.buggyFunc = buggyFunc;
        this.buggyFuncWithFL = buggyFuncWithFL;
        this.methodSignature = methodSignature;
        this.tests = tests;
        this.javadocString = javadocString;
    }

    public JsonObject toJson() {
        JsonObject obj = new JsonObject();
        obj.addProperty("buggy_func", buggyFunc);
        obj.addProperty("buggy_func_with_fl", buggyFuncWithFL);
        obj.add("method_signature", methodSignature.toJson());
        obj.add("tests", tests);
        obj.addProperty("javadoc_string", javadocString);
        return obj;
    }
}
