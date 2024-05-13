package kr.ac.unist.loft.srepairextractor;

import java.io.File;
import java.io.IOException;
import java.nio.charset.Charset;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.github.javaparser.ast.body.ConstructorDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.Parameter;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import com.google.common.io.Files;
import com.google.gson.JsonObject;

public class MethodInfoVisitor extends VoidVisitorAdapter<Void> {
    private List<Location> locations;
    private String filePath;
    private String sourcePath;
    private Map<Location, LocationInfo> locationInfoMap=new HashMap<>();
    private JsonObject tests;
    private List<String> codeLines;

    public MethodInfoVisitor(List<Location> locations, String filePath,String sourcePath,JsonObject tests) throws IOException {
        this.locations = locations;
        this.filePath = filePath;
        this.sourcePath = sourcePath;
        this.tests = tests;

        codeLines=Files.readLines(new File(filePath), Charset.defaultCharset());
    }

    @Override
    public void visit(MethodDeclaration n, Void arg) {
        super.visit(n, arg);

        for (Location location : locations) {
            if (filePath.equals(sourcePath+"/"+location.file+".java") && location.line >= n.getBegin().get().line &&
                    location.line <= n.getEnd().get().line) {
                String paramString="";
                for (Parameter param:n.getParameters()) {
                    paramString+=param.getTypeAsString()+" "+param.getNameAsString()+", ";
                }
                if (paramString.length()>0) paramString=paramString.substring(0,paramString.length()-2);
                LocationInfo.MethodSignature methodSignature = new LocationInfo.MethodSignature(n.getTypeAsString(),
                                        n.getNameAsString(), paramString);

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
                        n.getJavadoc().isPresent()?n.getJavadoc().get().toComment().asString():"",n.getBegin().get().line,
                        n.getEnd().get().line, filePath,location);
                locationInfoMap.put(location, locationInfo);
            }
        }
    }

    @Override
    public void visit(ConstructorDeclaration n, Void arg) {
        super.visit(n, arg);

        for (Location location : locations) {
            if (filePath.equals(sourcePath+"/"+location.file+".java") && location.line >= n.getBegin().get().line &&
                    location.line <= n.getEnd().get().line) {
                String paramString="";
                for (Parameter param:n.getParameters()) {
                    paramString+=param.getTypeAsString()+" "+param.getNameAsString()+", ";
                }
                if (paramString.length()>0) paramString=paramString.substring(0,paramString.length()-2);
                LocationInfo.MethodSignature methodSignature = new LocationInfo.MethodSignature("void",
                                n.getNameAsString(), paramString);

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
                        n.getJavadoc().isPresent()?n.getJavadoc().get().toComment().asString():"",n.getBegin().get().line,
                        n.getEnd().get().line, filePath,location);
                locationInfoMap.put(location, locationInfo);
            }
        }
    }


    public Map<Location, LocationInfo> getLocationInfoMap() {
        return locationInfoMap;
    }
}
