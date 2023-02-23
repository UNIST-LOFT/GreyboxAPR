package edu.lu.uni.serval.main;

import java.io.File;

import edu.lu.uni.serval.bug.fixer.AbstractFixer;
import edu.lu.uni.serval.bug.fixer.kParFixer_NFL;
import edu.lu.uni.serval.config.Configuration;

/**
 * Fix bugs with Fault Localization results reported with another version of GZoltar.
 * 
 * @author kui.liu
 *
 */
public class Main_NFL {
	
	public static void main(String[] args) {
		if (args.length != 5) {
			System.out.println("Arguments: <Failed_Test_Cases_File_Path> <Suspicious_Code_Positions_File_Path> <Buggy_Project_Path> <defects4j_Path> <Project_Name>");
			System.exit(0);
		}
		Configuration.failedTestCasesFilePath = args[0];
		Configuration.suspPositionsFilePath = args[1];
		String buggyProjectsPath = args[2];// "../Defects4JData/"
		String defects4jPath = args[3]; // "../defects4j/"
		String projectName = args[4]; // "Chart_1"
		Configuration.outputPath += "NFL/";
		System.out.println(projectName);
		fixBug(buggyProjectsPath, defects4jPath, projectName);
	}

	public static void fixBug(String buggyProjectsPath, String defects4jPath, String buggyProjectName) {
		String suspiciousFileStr = Configuration.suspPositionsFilePath;
		
		String dataType = "kPAR";
		String[] elements = buggyProjectName.split("_");
		String projectName = elements[0];
		int bugId;
		try {
			bugId = Integer.valueOf(elements[1]);
		} catch (NumberFormatException e) {
			System.err.println("Please input correct buggy project ID, such as \"Chart_1\".");
			return;
		}
		
		AbstractFixer fixer = new kParFixer_NFL(buggyProjectsPath, projectName, bugId, defects4jPath);
		fixer.metric = Configuration.faultLocalizationMetric;
		fixer.dataType = dataType;
		fixer.suspCodePosFile = new File(suspiciousFileStr);
		if (Integer.MAX_VALUE == fixer.minErrorTest) {
			System.out.println("Failed to defects4j compile bug " + buggyProjectName);
			return;
		}
		
		fixer.fixProcess();
		
		int fixedStatus = fixer.fixedStatus;
		switch (fixedStatus) {
		case 0:
			System.out.println("Failed to fix bug " + buggyProjectName);
			break;
		case 1:
			System.out.println("Succeeded to fix bug " + buggyProjectName);
			break;
		case 2:
			System.out.println("Partial succeeded to fix bug " + buggyProjectName);
			break;
		}
	}

}
