package kr.ac.unist.loft.srepairextractor;

import java.io.File;
import java.io.IOException;
import java.nio.charset.Charset;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import com.google.common.io.Files;
import com.google.gson.JsonObject;

public class MethodInfoVisitor extends VoidVisitorAdapter<Void> {
    private List<Location> locations;
    private String filePath;
    private Map<Location, LocationInfo> locationInfoMap=new HashMap<>();
    private JsonObject tests;
    private List<String> codeLines;

    public MethodInfoVisitor(List<Location> locations, String filePath,JsonObject tests) throws IOException {
        this.locations = locations;
        this.filePath = filePath;
        this.tests = tests;

        codeLines=Files.readLines(new File(filePath), Charset.defaultCharset());
    }

    @Override
    public void visit(MethodDeclaration n, Void arg) {
        super.visit(n, arg);

        for (Location location : locations) {
            if (location.file.equals(filePath) && location.line >= n.getBegin().get().line &&
                    location.line <= n.getEnd().get().line) {
                // TODO: Check Parameters.toString() returns correct string
                LocationInfo.MethodSignature methodSignature = new LocationInfo.MethodSignature(n.getTypeAsString(),
                                        n.getNameAsString(), n.getParameters().toString());

                String buggyFunc="";
                String buggyFuncWithFL="";
                for (int i=n.getBegin().get().line-1;i<n.getEnd().get().line;i++){
                    buggyFunc+=codeLines.get(i)+"\n";
                    if (i==location.line-1){
                        buggyFuncWithFL+=codeLines.get(i)+" /* bug is here */\n";
                    }else{
                        buggyFuncWithFL+=codeLines.get(i)+"\n";
                    }
                }
                LocationInfo locationInfo = new LocationInfo(buggyFunc, buggyFuncWithFL, methodSignature, tests,
                                    n.getJavadoc().get().toComment().asString());
                locationInfoMap.put(location, locationInfo);
            }
        }
    }

    public Map<Location, LocationInfo> getLocationInfoMap() {
        return locationInfoMap;
    }
}
