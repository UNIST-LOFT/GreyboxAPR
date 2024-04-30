/**
 * Scaffolding file used to store all the setups needed to run 
 * tests automatically generated by EvoSuite
 * Sat Dec 28 00:14:00 GMT 2019
 */

package org.apache.commons.math3.fitting.leastsquares;

import org.evosuite.runtime.annotation.EvoSuiteClassExclude;
import org.junit.BeforeClass;
import org.junit.Before;
import org.junit.After;
import org.junit.AfterClass;
import org.evosuite.runtime.sandbox.Sandbox;
import org.evosuite.runtime.sandbox.Sandbox.SandboxMode;

import static org.evosuite.shaded.org.mockito.Mockito.*;
@EvoSuiteClassExclude
public class LevenbergMarquardtOptimizer_ESTest_scaffolding {

  @org.junit.Rule 
  public org.evosuite.runtime.vnet.NonFunctionalRequirementRule nfr = new org.evosuite.runtime.vnet.NonFunctionalRequirementRule();

  private static final java.util.Properties defaultProperties = (java.util.Properties) java.lang.System.getProperties().clone(); 

  private org.evosuite.runtime.thread.ThreadStopper threadStopper =  new org.evosuite.runtime.thread.ThreadStopper (org.evosuite.runtime.thread.KillSwitchHandler.getInstance(), 3000);


  @BeforeClass 
  public static void initEvoSuiteFramework() { 
    org.evosuite.runtime.RuntimeSettings.className = "org.apache.commons.math3.fitting.leastsquares.LevenbergMarquardtOptimizer"; 
    org.evosuite.runtime.GuiSupport.initialize(); 
    org.evosuite.runtime.RuntimeSettings.maxNumberOfThreads = 100; 
    org.evosuite.runtime.RuntimeSettings.maxNumberOfIterationsPerLoop = 10000; 
    org.evosuite.runtime.RuntimeSettings.mockSystemIn = true; 
    org.evosuite.runtime.RuntimeSettings.sandboxMode = org.evosuite.runtime.sandbox.Sandbox.SandboxMode.RECOMMENDED; 
    org.evosuite.runtime.sandbox.Sandbox.initializeSecurityManagerForSUT(); 
    org.evosuite.runtime.classhandling.JDKClassResetter.init();
    setSystemProperties();
    initializeClasses();
    org.evosuite.runtime.Runtime.getInstance().resetRuntime(); 
    try { initMocksToAvoidTimeoutsInTheTests(); } catch(ClassNotFoundException e) {} 
  } 

  @AfterClass 
  public static void clearEvoSuiteFramework(){ 
    Sandbox.resetDefaultSecurityManager(); 
    java.lang.System.setProperties((java.util.Properties) defaultProperties.clone()); 
  } 

  @Before 
  public void initTestCase(){ 
    threadStopper.storeCurrentThreads();
    threadStopper.startRecordingTime();
    org.evosuite.runtime.jvm.ShutdownHookHandler.getInstance().initHandler(); 
    org.evosuite.runtime.sandbox.Sandbox.goingToExecuteSUTCode(); 
    setSystemProperties(); 
    org.evosuite.runtime.GuiSupport.setHeadless(); 
    org.evosuite.runtime.Runtime.getInstance().resetRuntime(); 
    org.evosuite.runtime.agent.InstrumentingAgent.activate(); 
  } 

  @After 
  public void doneWithTestCase(){ 
    threadStopper.killAndJoinClientThreads();
    org.evosuite.runtime.jvm.ShutdownHookHandler.getInstance().safeExecuteAddedHooks(); 
    org.evosuite.runtime.classhandling.JDKClassResetter.reset(); 
    resetClasses(); 
    org.evosuite.runtime.sandbox.Sandbox.doneWithExecutingSUTCode(); 
    org.evosuite.runtime.agent.InstrumentingAgent.deactivate(); 
    org.evosuite.runtime.GuiSupport.restoreHeadlessMode(); 
  } 

  public static void setSystemProperties() {
 
    java.lang.System.setProperties((java.util.Properties) defaultProperties.clone()); 
    java.lang.System.setProperty("file.encoding", "UTF-8"); 
    java.lang.System.setProperty("java.awt.headless", "true"); 
    java.lang.System.setProperty("java.io.tmpdir", "/tmp"); 
    java.lang.System.setProperty("user.country", "US"); 
    java.lang.System.setProperty("user.dir", "/home/wasp/Desktop/research/evosuite-bugjar/tests/bugs-dot-jar_MATH-1106_e2dc384d/1"); 
    java.lang.System.setProperty("user.home", "/home/wasp"); 
    java.lang.System.setProperty("user.language", "en"); 
    java.lang.System.setProperty("user.name", "wasp"); 
    java.lang.System.setProperty("user.timezone", "America/Los_Angeles"); 
  }

  private static void initializeClasses() {
    org.evosuite.runtime.classhandling.ClassStateSupport.initializeClasses(LevenbergMarquardtOptimizer_ESTest_scaffolding.class.getClassLoader() ,
      "org.apache.commons.math3.analysis.differentiation.MultivariateDifferentiableVectorFunction",
      "org.apache.commons.math3.linear.RealVectorFormat",
      "org.apache.commons.math3.optim.OptimizationProblem",
      "org.apache.commons.math3.linear.RealVector",
      "org.apache.commons.math3.analysis.function.Constant",
      "org.apache.commons.math3.exception.util.ArgUtils",
      "org.apache.commons.math3.exception.MathArithmeticException",
      "org.apache.commons.math3.analysis.polynomials.PolynomialFunctionNewtonForm",
      "org.apache.commons.math3.analysis.function.Cos",
      "org.apache.commons.math3.analysis.differentiation.DSCompiler",
      "org.apache.commons.math3.RealFieldElement",
      "org.apache.commons.math3.exception.MathIllegalArgumentException",
      "org.apache.commons.math3.analysis.FunctionUtils",
      "org.apache.commons.math3.exception.ConvergenceException",
      "org.apache.commons.math3.util.FastMath",
      "org.apache.commons.math3.FieldElement",
      "org.apache.commons.math3.analysis.function.Acos",
      "org.apache.commons.math3.analysis.differentiation.MultivariateDifferentiableFunction",
      "org.apache.commons.math3.linear.RealVector$Entry",
      "org.apache.commons.math3.analysis.differentiation.UnivariateDifferentiableFunction",
      "org.apache.commons.math3.linear.RealMatrix",
      "org.apache.commons.math3.exception.NotFiniteNumberException",
      "org.apache.commons.math3.analysis.function.Sinh",
      "org.apache.commons.math3.analysis.MultivariateMatrixFunction",
      "org.apache.commons.math3.analysis.DifferentiableMultivariateVectorFunction",
      "org.apache.commons.math3.exception.util.ExceptionContextProvider",
      "org.apache.commons.math3.util.MathArrays",
      "org.apache.commons.math3.analysis.polynomials.PolynomialSplineFunction",
      "org.apache.commons.math3.util.MathArrays$1",
      "org.apache.commons.math3.util.MathArrays$2",
      "org.apache.commons.math3.util.MathArrays$3",
      "org.apache.commons.math3.analysis.function.Sqrt",
      "org.apache.commons.math3.exception.NumberIsTooSmallException",
      "org.apache.commons.math3.exception.MathIllegalStateException",
      "org.apache.commons.math3.linear.NonSquareMatrixException",
      "org.apache.commons.math3.analysis.polynomials.PolynomialFunction",
      "org.apache.commons.math3.analysis.function.Multiply",
      "org.apache.commons.math3.analysis.polynomials.PolynomialFunctionLagrangeForm",
      "org.apache.commons.math3.linear.Array2DRowRealMatrix",
      "org.apache.commons.math3.util.MathUtils",
      "org.apache.commons.math3.util.CompositeFormat",
      "org.apache.commons.math3.exception.util.LocalizedFormats",
      "org.apache.commons.math3.util.Pair",
      "org.apache.commons.math3.linear.AbstractRealMatrix",
      "org.apache.commons.math3.util.Incrementor$MaxCountExceededCallback",
      "org.apache.commons.math3.exception.MathParseException",
      "org.apache.commons.math3.fitting.leastsquares.LeastSquaresProblem$Evaluation",
      "org.apache.commons.math3.fitting.leastsquares.LeastSquaresProblem",
      "org.apache.commons.math3.exception.DimensionMismatchException",
      "org.apache.commons.math3.linear.RealVector$2$UnmodifiableEntry",
      "org.apache.commons.math3.exception.util.ExceptionContext",
      "org.apache.commons.math3.optim.ConvergenceChecker",
      "org.apache.commons.math3.linear.RealVectorChangingVisitor",
      "org.apache.commons.math3.linear.RealVectorPreservingVisitor",
      "org.apache.commons.math3.analysis.function.StepFunction",
      "org.apache.commons.math3.linear.RealVector$1",
      "org.apache.commons.math3.linear.RealVector$2",
      "org.apache.commons.math3.util.Precision",
      "org.apache.commons.math3.analysis.DifferentiableUnivariateFunction",
      "org.apache.commons.math3.analysis.DifferentiableMultivariateFunction",
      "org.apache.commons.math3.analysis.function.Cbrt",
      "org.apache.commons.math3.analysis.differentiation.DerivativeStructure",
      "org.apache.commons.math3.exception.OutOfRangeException",
      "org.apache.commons.math3.exception.NotPositiveException",
      "org.apache.commons.math3.exception.MathInternalError",
      "org.apache.commons.math3.analysis.function.Divide",
      "org.apache.commons.math3.exception.NonMonotonicSequenceException",
      "org.apache.commons.math3.linear.ArrayRealVector",
      "org.apache.commons.math3.linear.RealVector$SparseEntryIterator",
      "org.apache.commons.math3.analysis.function.Sigmoid",
      "org.apache.commons.math3.exception.MathUnsupportedOperationException",
      "org.apache.commons.math3.analysis.function.Ceil",
      "org.apache.commons.math3.linear.RealMatrixFormat",
      "org.apache.commons.math3.analysis.MultivariateVectorFunction",
      "org.apache.commons.math3.util.MathArrays$Position",
      "org.apache.commons.math3.linear.SparseRealMatrix",
      "org.apache.commons.math3.exception.NumberIsTooLargeException",
      "org.apache.commons.math3.analysis.function.Signum",
      "org.apache.commons.math3.analysis.BivariateFunction",
      "org.apache.commons.math3.exception.NotStrictlyPositiveException",
      "org.apache.commons.math3.exception.NoDataException",
      "org.apache.commons.math3.linear.SparseRealVector",
      "org.apache.commons.math3.analysis.UnivariateFunction",
      "org.apache.commons.math3.analysis.MultivariateFunction",
      "org.apache.commons.math3.linear.RealLinearOperator",
      "org.apache.commons.math3.linear.RealMatrixPreservingVisitor",
      "org.apache.commons.math3.analysis.function.Inverse",
      "org.apache.commons.math3.analysis.function.Atan",
      "org.apache.commons.math3.util.OpenIntToDoubleHashMap",
      "org.apache.commons.math3.linear.OpenMapRealMatrix",
      "org.apache.commons.math3.fitting.leastsquares.LevenbergMarquardtOptimizer",
      "org.apache.commons.math3.util.MathArrays$OrderDirection",
      "org.apache.commons.math3.linear.OpenMapRealVector",
      "org.apache.commons.math3.linear.MatrixDimensionMismatchException",
      "org.apache.commons.math3.fitting.leastsquares.LeastSquaresAdapter",
      "org.apache.commons.math3.util.OpenIntToDoubleHashMap$Iterator",
      "org.apache.commons.math3.analysis.FunctionUtils$13",
      "org.apache.commons.math3.exception.MultiDimensionMismatchException",
      "org.apache.commons.math3.util.Incrementor",
      "org.apache.commons.math3.exception.MathIllegalNumberException",
      "org.apache.commons.math3.linear.AnyMatrix",
      "org.apache.commons.math3.exception.MaxCountExceededException",
      "org.apache.commons.math3.exception.util.Localizable",
      "org.apache.commons.math3.fitting.leastsquares.LevenbergMarquardtOptimizer$InternalData",
      "org.apache.commons.math3.linear.RealVector$2$1",
      "org.apache.commons.math3.random.RandomGenerator",
      "org.apache.commons.math3.exception.NullArgumentException",
      "org.apache.commons.math3.Field",
      "org.apache.commons.math3.fitting.leastsquares.LeastSquaresOptimizer",
      "org.apache.commons.math3.linear.RealMatrixChangingVisitor",
      "org.apache.commons.math3.fitting.leastsquares.LeastSquaresOptimizer$Optimum"
    );
  } 
  private static void initMocksToAvoidTimeoutsInTheTests() throws ClassNotFoundException { 
    mock(Class.forName("org.apache.commons.math3.fitting.leastsquares.LeastSquaresProblem", false, LevenbergMarquardtOptimizer_ESTest_scaffolding.class.getClassLoader()));
    mock(Class.forName("org.apache.commons.math3.optim.ConvergenceChecker", false, LevenbergMarquardtOptimizer_ESTest_scaffolding.class.getClassLoader()));
    mock(Class.forName("org.apache.commons.math3.util.Incrementor", false, LevenbergMarquardtOptimizer_ESTest_scaffolding.class.getClassLoader()));
  }

  private static void resetClasses() {
    org.evosuite.runtime.classhandling.ClassResetter.getInstance().setClassLoader(LevenbergMarquardtOptimizer_ESTest_scaffolding.class.getClassLoader()); 

    org.evosuite.runtime.classhandling.ClassStateSupport.resetClasses(
      "org.apache.commons.math3.util.Precision",
      "org.apache.commons.math3.fitting.leastsquares.LevenbergMarquardtOptimizer",
      "org.apache.commons.math3.fitting.leastsquares.LevenbergMarquardtOptimizer$InternalData",
      "org.apache.commons.math3.exception.util.LocalizedFormats",
      "org.apache.commons.math3.fitting.leastsquares.LeastSquaresAdapter",
      "org.apache.commons.math3.linear.RealVector",
      "org.apache.commons.math3.linear.SparseRealVector",
      "org.apache.commons.math3.linear.OpenMapRealVector",
      "org.apache.commons.math3.util.OpenIntToDoubleHashMap",
      "org.apache.commons.math3.util.FastMath",
      "org.apache.commons.math3.linear.RealVectorFormat",
      "org.apache.commons.math3.util.CompositeFormat",
      "org.apache.commons.math3.linear.ArrayRealVector",
      "org.apache.commons.math3.exception.MathIllegalArgumentException",
      "org.apache.commons.math3.exception.NullArgumentException",
      "org.apache.commons.math3.exception.util.ExceptionContext",
      "org.apache.commons.math3.exception.util.ArgUtils",
      "org.apache.commons.math3.linear.RealVector$2",
      "org.apache.commons.math3.exception.MathArithmeticException",
      "org.apache.commons.math3.exception.MathIllegalNumberException",
      "org.apache.commons.math3.exception.DimensionMismatchException",
      "org.apache.commons.math3.linear.RealVector$1",
      "org.apache.commons.math3.linear.RealVector$Entry",
      "org.apache.commons.math3.util.OpenIntToDoubleHashMap$Iterator",
      "org.apache.commons.math3.exception.NumberIsTooLargeException",
      "org.apache.commons.math3.util.Incrementor",
      "org.apache.commons.math3.exception.OutOfRangeException",
      "org.apache.commons.math3.analysis.function.Multiply",
      "org.apache.commons.math3.analysis.FunctionUtils",
      "org.apache.commons.math3.analysis.FunctionUtils$13",
      "org.apache.commons.math3.linear.RealVector$2$1",
      "org.apache.commons.math3.linear.RealVector$2$UnmodifiableEntry",
      "org.apache.commons.math3.exception.MathUnsupportedOperationException",
      "org.apache.commons.math3.linear.RealLinearOperator",
      "org.apache.commons.math3.linear.RealMatrixFormat",
      "org.apache.commons.math3.linear.AbstractRealMatrix",
      "org.apache.commons.math3.linear.OpenMapRealMatrix",
      "org.apache.commons.math3.exception.NumberIsTooSmallException",
      "org.apache.commons.math3.exception.NotStrictlyPositiveException",
      "org.apache.commons.math3.analysis.function.Divide",
      "org.apache.commons.math3.analysis.function.StepFunction",
      "org.apache.commons.math3.analysis.function.Signum",
      "org.apache.commons.math3.analysis.function.Cos",
      "org.apache.commons.math3.analysis.function.Sigmoid",
      "org.apache.commons.math3.analysis.function.Sinh",
      "org.apache.commons.math3.analysis.polynomials.PolynomialFunctionLagrangeForm",
      "org.apache.commons.math3.util.MathArrays$OrderDirection",
      "org.apache.commons.math3.util.MathArrays",
      "org.apache.commons.math3.util.MathArrays$Position",
      "org.apache.commons.math3.util.MathArrays$3",
      "org.apache.commons.math3.util.Pair",
      "org.apache.commons.math3.util.MathArrays$1",
      "org.apache.commons.math3.exception.NonMonotonicSequenceException",
      "org.apache.commons.math3.analysis.polynomials.PolynomialFunctionNewtonForm",
      "org.apache.commons.math3.util.MathUtils",
      "org.apache.commons.math3.analysis.polynomials.PolynomialFunction",
      "org.apache.commons.math3.analysis.polynomials.PolynomialSplineFunction",
      "org.apache.commons.math3.analysis.function.Inverse",
      "org.apache.commons.math3.analysis.function.Ceil",
      "org.apache.commons.math3.analysis.function.Acos",
      "org.apache.commons.math3.analysis.function.Sqrt",
      "org.apache.commons.math3.analysis.function.Constant",
      "org.apache.commons.math3.analysis.differentiation.DerivativeStructure",
      "org.apache.commons.math3.analysis.differentiation.DSCompiler",
      "org.apache.commons.math3.analysis.function.Cbrt",
      "org.apache.commons.math3.analysis.function.Atan"
    );
  }
}