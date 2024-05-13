package kr.ac.unist.loft.srepairextractor;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;

import com.google.common.base.Charsets;
import com.google.common.io.Files;

public class Main {
    public static void main(String[] args) {
        if (args.length != 5) {
            System.exit(1);
        }
        Options options = new Options();
        CommandLineParser parser = new DefaultParser();
        CommandLine cmd=null;
        try {
            cmd = parser.parse(options, args);
        } catch (ParseException e) {
            e.printStackTrace();
            System.exit(1);
        }
        String[] arguments=cmd.getArgs();

        try{
            // Parser FL file
            String flResultPath = arguments[0];
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

            
        } catch (IOException e) {
            e.printStackTrace();
            System.exit(1);
        }
    }
}
