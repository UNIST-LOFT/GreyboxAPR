package kr.ac.unist.loft.srepairextractor;

import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.charset.Charset;
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
import com.google.common.io.Files;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.google.gson.stream.JsonWriter;

public class Main {
    static final Logger LOGGER=Logger.getGlobal();

    public static void main(String[] args) {
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
        if (cmd.hasOption("d")) LOGGER.setLevel(Level.FINER);
        else LOGGER.setLevel(Level.INFO);

        String[] arguments=cmd.getArgs();
        if (arguments.length != 5) {
            System.err.println("Usage: java -jar SRepairExtractor.jar [-d] <fl_result_file> <source path> <dataset_path> <project> <output_path>");
            System.exit(1);
        }

        try{
            // Parser FL file
            String flResultPath = arguments[0];
            LOGGER.info("FL result file: "+flResultPath);

            List<Location> locations=new ArrayList<>();
            // Read the FL result file
            List<String> lines;
            File flResultFile=new File(flResultPath);
            if (flResultFile.exists())
                lines=Files.readLines(flResultFile, Charset.defaultCharset());
            else
                lines=Files.readLines(new File(flResultPath.replace("Ochiai", "ochiai")), Charset.defaultCharset());
            for (String line : lines) {
                String[] tokens = line.split("@");
                String file = tokens[0].replace('.', '/');
                int lineNum = Integer.parseInt(tokens[1]);
                float score = Float.parseFloat(tokens[2]);
                Location loc = new Location(file, lineNum, score);
                locations.add(loc);
            }

            String sourcePath=arguments[1];
            if (sourcePath.endsWith("/")) sourcePath=sourcePath.substring(0,sourcePath.length()-1);
            LOGGER.info("Source path: "+sourcePath);
            // Compile suitable source files
            Map<String,CompilationUnit> cuMap=new HashMap<>();
            for (Location loc:locations){
                String file=loc.file;
                if (!cuMap.containsKey(file)){
                    File srcFile = new File(sourcePath+"/"+file+".java");
                    if (!srcFile.exists()) {
                        LOGGER.warning("File not found: "+file+", skipping");
                        continue;
                    }
                    CompilationUnit cu = StaticJavaParser.parse(new FileReader(srcFile));
                    cuMap.put(srcFile.getAbsolutePath(), cu);
                }
            }

            // Read failing tests from SRepair dataset
            String datasetPath=arguments[2];
            String project=arguments[3];
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
                MethodInfoVisitor methodInfoVisitor=new MethodInfoVisitor(locations, file, sourcePath, failingTests);
                methodInfoVisitor.visit(cu, null);
                locationInfoMap.putAll(methodInfoVisitor.getLocationInfoMap());
            }

            // Save loc info to file
            String outputFilePath=arguments[4];
            LOGGER.info("Output file path: "+outputFilePath);
            if (java.nio.file.Files.notExists(new File(outputFilePath+"/"+project).toPath()))
                java.nio.file.Files.createDirectory(new File(outputFilePath+"/"+project).toPath());
            if (java.nio.file.Files.notExists(new File(outputFilePath+"/"+project+"/input").toPath()))
                java.nio.file.Files.createDirectory(new File(outputFilePath+"/"+project+"/input").toPath());
            
            for (int i=0;i<locations.size();i++){
                Location loc=locations.get(i);
                if (!locationInfoMap.containsKey(loc)){
                    LOGGER.fine("Location not found: "+loc+", it may not in the method");
                    continue;
                }
                LocationInfo locInfo=locationInfoMap.get(loc);
                JsonObject locObj=locInfo.toJson();
                JsonObject newObj=new JsonObject();
                newObj.add(project, locObj);

                FileWriter writer=new FileWriter(outputFilePath+"/"+project+"/input/"+i+".json");
                Gson gson=new GsonBuilder().setPrettyPrinting().disableHtmlEscaping().create();
                JsonWriter jsonWriter=gson.newJsonWriter(writer);
                jsonWriter.setIndent("  ");
                gson.toJson(newObj,jsonWriter);
                writer.close();
            }
        } catch (IOException e) {
            e.printStackTrace();
            System.exit(1);
        }
    }
}
