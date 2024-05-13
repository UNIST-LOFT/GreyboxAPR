package kr.ac.unist.loft.srepairextractor;

import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;

import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.google.common.base.Charsets;
import com.google.common.io.Files;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

public class Main {
    static final Logger LOGGER=Logger.getGlobal();

    public static void main(String[] args) {
        if (args.length != 5) {
            System.err.println("Usage: java -jar SRepairExtractor.jar [-d] <fl_result_file> <dataset_path> <project> <output_path>");
            System.exit(1);
        }
        Options options = new Options();
        options.addOption(new Option("d", "debug", false, "print debug information"));

        CommandLineParser parser = new DefaultParser();
        CommandLine cmd=null;
        try {
            cmd = parser.parse(options, args);
        } catch (ParseException e) {
            e.printStackTrace();
            System.exit(1);
        }
        if (cmd.hasOption("d")) LOGGER.setLevel(Level.ALL);
        else LOGGER.setLevel(Level.INFO);

        String[] arguments=cmd.getArgs();

        try{
            // Parser FL file
            String flResultPath = arguments[0];
            LOGGER.info("FL result file: "+flResultPath);

            List<Location> locations=new ArrayList<>();
            // Read the FL result file
            List<String> lines=Files.readLines(new File(flResultPath), Charsets.UTF_8);
            for (String line : lines) {
                String[] tokens = line.split("@");
                String file = tokens[0].replace('.', '/');
                int lineNum = Integer.parseInt(tokens[1]);
                float score = Float.parseFloat(tokens[2]);
                Location loc = new Location(file, lineNum, score);
                locations.add(loc);
            }

            // Compile suitable source files
            Map<String,CompilationUnit> cuMap=new HashMap<>();
            for (Location loc:locations){
                String file=loc.file;
                if (!cuMap.containsKey(file)){
                    File srcFile = new File(file);
                    if (!srcFile.exists()) {
                        System.exit(1);
                    }
                    CompilationUnit cu = StaticJavaParser.parse(new FileReader(srcFile));
                    cuMap.put(file, cu);
                }
            }

            // Read failing tests from SRepair dataset
            String datasetPath=arguments[1];
            String project=arguments[2];
            LOGGER.info("SRepair dataset path: "+datasetPath);
            LOGGER.info("Project: "+project);

            JsonObject root=JsonParser.parseReader(new FileReader(datasetPath+"/defects4j-sf.json")).getAsJsonObject();
            JsonObject failingTests=null;
            if (root.has(project.replace('_', '-'))) {
                JsonObject projectObj = root.getAsJsonObject(project.replace('_', '-'));
                failingTests = projectObj.getAsJsonObject("trigger_test");
            }
            else {
                root=JsonParser.parseReader(new FileReader(datasetPath+"/defects4j-mf.json")).getAsJsonObject();
                JsonObject projectObj=root.getAsJsonObject(project.replace('_', '-'));
                failingTests=projectObj.getAsJsonObject("trigger_test");
            }

            // Get location infos
            Map<Location, LocationInfo> locationInfoMap=new HashMap<>();
            for (Map.Entry<String,CompilationUnit> entry:cuMap.entrySet()){
                String file=entry.getKey();
                CompilationUnit cu=entry.getValue();
                MethodInfoVisitor methodInfoVisitor=new MethodInfoVisitor(locations, file, failingTests);
                methodInfoVisitor.visit(cu, null);
                locationInfoMap.putAll(methodInfoVisitor.getLocationInfoMap());
            }

            // Save loc info to file
            String outputFilePath=arguments[3];
            LOGGER.info("Output file path: "+outputFilePath);
            if (java.nio.file.Files.notExists(new File(outputFilePath+"/"+project).toPath()))
                java.nio.file.Files.createDirectory(new File(outputFilePath).toPath());
            
            for (int i=0;i<locations.size();i++){
                Location loc=locations.get(i);
                LocationInfo locInfo=locationInfoMap.get(loc);
                JsonObject locObj=locInfo.toJson();

                FileWriter writer=new FileWriter(outputFilePath+"/"+project+"/"+i+".json");
                writer.write(locObj.toString());
                writer.close();
            }
        } catch (IOException e) {
            e.printStackTrace();
            System.exit(1);
        }
    }
}
