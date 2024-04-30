/*
 * This file was automatically generated by EvoSuite
 * Fri Dec 27 23:43:05 GMT 2019
 */

package org.apache.commons.math3.distribution;

import org.junit.Test;
import static org.junit.Assert.*;
import static org.evosuite.runtime.EvoAssertions.*;
import org.apache.commons.math3.distribution.BinomialDistribution;
import org.apache.commons.math3.random.RandomGenerator;
import org.apache.commons.math3.random.SynchronizedRandomGenerator;
import org.apache.commons.math3.random.Well19937a;
import org.apache.commons.math3.random.Well19937c;
import org.apache.commons.math3.random.Well44497a;
import org.apache.commons.math3.random.Well512a;
import org.evosuite.runtime.EvoRunner;
import org.evosuite.runtime.EvoRunnerParameters;
import org.junit.runner.RunWith;

@RunWith(EvoRunner.class) @EvoRunnerParameters(mockJVMNonDeterminism = true, useVFS = true, useVNET = true, resetStaticState = true, separateClassLoader = true, useJEE = true) 
public class BinomialDistribution_ESTest extends BinomialDistribution_ESTest_scaffolding {

  @Test(timeout = 4000)
  public void test00()  throws Throwable  {
      BinomialDistribution binomialDistribution0 = new BinomialDistribution(1, 1);
      binomialDistribution0.cumulativeProbability(1, 1);
      binomialDistribution0.reseedRandomGenerator((-3132L));
      binomialDistribution0.cumulativeProbability(1);
      binomialDistribution0.getProbabilityOfSuccess();
      binomialDistribution0.sample();
      binomialDistribution0.getSupportLowerBound();
      binomialDistribution0.cumulativeProbability(0);
      binomialDistribution0.cumulativeProbability(1);
      binomialDistribution0.cumulativeProbability(1, 1);
      binomialDistribution0.getNumericalVariance();
      binomialDistribution0.isSupportConnected();
      binomialDistribution0.logProbability(1634);
      binomialDistribution0.isSupportConnected();
  }

  @Test(timeout = 4000)
  public void test01()  throws Throwable  {
      Well44497a well44497a0 = new Well44497a(1092);
      BinomialDistribution binomialDistribution0 = new BinomialDistribution(well44497a0, 1092, 1.2076238768270153E-8);
      well44497a0.nextGaussian();
      binomialDistribution0.cumulativeProbability(1092);
      binomialDistribution0.cumulativeProbability((-1));
      binomialDistribution0.cumulativeProbability((-1202));
      binomialDistribution0.getNumberOfTrials();
      well44497a0.nextFloat();
      binomialDistribution0.cumulativeProbability(0);
      binomialDistribution0.probability(0);
      binomialDistribution0.logProbability(0);
      binomialDistribution0.getNumericalVariance();
      binomialDistribution0.getProbabilityOfSuccess();
      binomialDistribution0.probability(1092);
      binomialDistribution0.sample(591);
      binomialDistribution0.isSupportConnected();
      binomialDistribution0.getNumberOfTrials();
      well44497a0.nextDouble();
      binomialDistribution0.isSupportConnected();
      binomialDistribution0.getProbabilityOfSuccess();
  }

  @Test(timeout = 4000)
  public void test02()  throws Throwable  {
      BinomialDistribution binomialDistribution0 = new BinomialDistribution(0, 0);
      binomialDistribution0.cumulativeProbability((-1));
      binomialDistribution0.getNumericalMean();
      binomialDistribution0.getNumberOfTrials();
      binomialDistribution0.logProbability((-2695));
      binomialDistribution0.probability(231);
      binomialDistribution0.getNumberOfTrials();
      binomialDistribution0.getNumericalVariance();
  }

  @Test(timeout = 4000)
  public void test03()  throws Throwable  {
      BinomialDistribution binomialDistribution0 = new BinomialDistribution(3235, 0.0);
      binomialDistribution0.reseedRandomGenerator(3235);
      binomialDistribution0.logProbability(3235);
      binomialDistribution0.solveInverseCumulativeProbability(0.0, 0, 0);
      binomialDistribution0.inverseCumulativeProbability(0.0);
      double double0 = binomialDistribution0.cumulativeProbability(0);
      binomialDistribution0.probability(0);
      binomialDistribution0.isSupportConnected();
      binomialDistribution0.getNumericalMean();
      double double1 = binomialDistribution0.logProbability((-4099));
      assertEquals(Double.NEGATIVE_INFINITY, double1, 0.01);
      
      double double2 = binomialDistribution0.probability(0);
      assertEquals(double2, double0, 0.01);
      
      double double3 = binomialDistribution0.getNumericalMean();
      assertEquals(0.0, double3, 0.01);
      
      int int0 = binomialDistribution0.inverseCumulativeProbability(0);
      assertEquals(0, int0);
      
      boolean boolean0 = binomialDistribution0.isSupportConnected();
      assertTrue(boolean0);
      
      binomialDistribution0.getSupportUpperBound();
      double double4 = binomialDistribution0.getProbabilityOfSuccess();
      assertEquals(0.0, double4, 0.01);
      assertEquals(3235, binomialDistribution0.getNumberOfTrials());
  }

  @Test(timeout = 4000)
  public void test04()  throws Throwable  {
      Well19937a well19937a0 = new Well19937a(0L);
      BinomialDistribution binomialDistribution0 = new BinomialDistribution(well19937a0, 732, 0L);
      double double0 = binomialDistribution0.logProbability(1372);
      assertEquals(Double.NEGATIVE_INFINITY, double0, 0.01);
      
      double double1 = binomialDistribution0.probability(732);
      assertEquals(0.0, double1, 0.01);
      
      int int0 = binomialDistribution0.getNumberOfTrials();
      assertEquals(732, int0);
      
      binomialDistribution0.getSupportUpperBound();
      assertEquals(0.0, binomialDistribution0.getProbabilityOfSuccess(), 0.01);
  }

  @Test(timeout = 4000)
  public void test05()  throws Throwable  {
      int int0 = 133;
      BinomialDistribution binomialDistribution0 = new BinomialDistribution(133, 0.172672301530838);
      binomialDistribution0.probability((-1));
      int int1 = 255;
      // Undeclared exception!
      binomialDistribution0.sample(255);
  }

  @Test(timeout = 4000)
  public void test06()  throws Throwable  {
      BinomialDistribution binomialDistribution0 = null;
      try {
        binomialDistribution0 = new BinomialDistribution((RandomGenerator) null, 0, (-2357.7958690331));
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // -2,357.796 out of [0, 1] range
         //
         verifyException("org.apache.commons.math3.distribution.BinomialDistribution", e);
      }
  }

  @Test(timeout = 4000)
  public void test07()  throws Throwable  {
      Well19937a well19937a0 = new Well19937a(0);
      BinomialDistribution binomialDistribution0 = new BinomialDistribution(well19937a0, 0, 0);
      int[] intArray0 = binomialDistribution0.sample(1486);
      double double0 = binomialDistribution0.cumulativeProbability((-169), 1065);
      assertEquals(1.0, double0, 0.01);
      
      double double1 = binomialDistribution0.cumulativeProbability(0);
      assertEquals(1.0, double1, 0.01);
      
      double double2 = binomialDistribution0.probability(1486);
      assertEquals(0.0, double2, 0.01);
      
      well19937a0.nextBoolean();
      double double3 = binomialDistribution0.getNumericalVariance();
      assertEquals(0.0, double3, 0.01);
      
      well19937a0.nextGaussian();
      well19937a0.setSeed((-1L));
      binomialDistribution0.getSupportLowerBound();
      well19937a0.setSeed(intArray0);
      boolean boolean0 = binomialDistribution0.isSupportConnected();
      assertTrue(boolean0);
      
      int int0 = binomialDistribution0.getNumberOfTrials();
      assertEquals(0, int0);
      
      binomialDistribution0.getSupportUpperBound();
      assertEquals(0.0, binomialDistribution0.getNumericalMean(), 0.01);
  }

  @Test(timeout = 4000)
  public void test08()  throws Throwable  {
      BinomialDistribution binomialDistribution0 = new BinomialDistribution(1430, 0.0);
      binomialDistribution0.sample();
      double double0 = binomialDistribution0.cumulativeProbability(0);
      assertEquals(1.0, double0, 0.01);
      
      binomialDistribution0.solveInverseCumulativeProbability(0.0, 0, 1430);
      binomialDistribution0.cumulativeProbability(1430, 1430);
      binomialDistribution0.sample();
      double double1 = binomialDistribution0.cumulativeProbability(1430);
      assertEquals(double1, double0, 0.01);
      
      double double2 = binomialDistribution0.getNumericalVariance();
      assertEquals(0.0, double2, 0.01);
      
      binomialDistribution0.reseedRandomGenerator((-1L));
      assertEquals(0, binomialDistribution0.getSupportUpperBound());
      
      binomialDistribution0.sample(1430);
      binomialDistribution0.getNumericalMean();
      boolean boolean0 = binomialDistribution0.isSupportConnected();
      assertTrue(boolean0);
      
      double double3 = binomialDistribution0.getNumericalMean();
      assertEquals(0.0, double3, 0.01);
      
      double double4 = binomialDistribution0.getProbabilityOfSuccess();
      assertEquals(0.0, double4, 0.01);
      assertEquals(1430, binomialDistribution0.getNumberOfTrials());
      assertEquals(0, binomialDistribution0.getSupportLowerBound());
  }

  @Test(timeout = 4000)
  public void test09()  throws Throwable  {
      Well44497a well44497a0 = new Well44497a();
      int int0 = 663;
      BinomialDistribution binomialDistribution0 = null;
      try {
        binomialDistribution0 = new BinomialDistribution(well44497a0, 663, 1.142035961151123);
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // 1.142 out of [0, 1] range
         //
         verifyException("org.apache.commons.math3.distribution.BinomialDistribution", e);
      }
  }

  @Test(timeout = 4000)
  public void test10()  throws Throwable  {
      BinomialDistribution binomialDistribution0 = new BinomialDistribution(1, 1);
      binomialDistribution0.isSupportConnected();
      double double0 = binomialDistribution0.logProbability(1);
      assertEquals(-0.0, double0, 0.01);
      
      binomialDistribution0.sample();
      double double1 = binomialDistribution0.probability(1);
      double double2 = binomialDistribution0.probability(4961);
      assertEquals(0.0, double2, 0.01);
      
      double double3 = binomialDistribution0.getNumericalMean();
      assertEquals(double3, double1, 0.01);
      
      boolean boolean0 = binomialDistribution0.isSupportConnected();
      assertTrue(boolean0);
      
      int int0 = binomialDistribution0.getSupportUpperBound();
      assertEquals(0.0, binomialDistribution0.getNumericalVariance(), 0.01);
      assertEquals(1, int0);
      assertEquals(1, binomialDistribution0.getSupportLowerBound());
  }

  @Test(timeout = 4000)
  public void test11()  throws Throwable  {
      BinomialDistribution binomialDistribution0 = new BinomialDistribution(0, 0.0);
      double double0 = binomialDistribution0.cumulativeProbability(0);
      assertEquals(0.0, binomialDistribution0.getNumericalMean(), 0.01);
      assertEquals(1.0, double0, 0.01);
      assertEquals(0, binomialDistribution0.getNumberOfTrials());
  }

  @Test(timeout = 4000)
  public void test12()  throws Throwable  {
      int int0 = 778;
      BinomialDistribution binomialDistribution0 = null;
      try {
        binomialDistribution0 = new BinomialDistribution(778, 778);
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // 778 out of [0, 1] range
         //
         verifyException("org.apache.commons.math3.distribution.BinomialDistribution", e);
      }
  }

  @Test(timeout = 4000)
  public void test13()  throws Throwable  {
      Well512a well512a0 = new Well512a((-836L));
      int int0 = (-844);
      BinomialDistribution binomialDistribution0 = null;
      try {
        binomialDistribution0 = new BinomialDistribution(well512a0, (-844), (-836L));
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // number of trials (-844)
         //
         verifyException("org.apache.commons.math3.distribution.BinomialDistribution", e);
      }
  }

  @Test(timeout = 4000)
  public void test14()  throws Throwable  {
      BinomialDistribution binomialDistribution0 = null;
      try {
        binomialDistribution0 = new BinomialDistribution((-1), (-1));
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // number of trials (-1)
         //
         verifyException("org.apache.commons.math3.distribution.BinomialDistribution", e);
      }
  }

  @Test(timeout = 4000)
  public void test15()  throws Throwable  {
      int[] intArray0 = new int[1];
      intArray0[0] = 0;
      Well512a well512a0 = new Well512a(intArray0);
      BinomialDistribution binomialDistribution0 = new BinomialDistribution(well512a0, 0, 0);
      double double0 = binomialDistribution0.getProbabilityOfSuccess();
      assertEquals(0.0, double0, 0.01);
      
      binomialDistribution0.getNumberOfTrials();
      int int0 = binomialDistribution0.getNumberOfTrials();
      assertEquals(0, int0);
  }

  @Test(timeout = 4000)
  public void test16()  throws Throwable  {
      BinomialDistribution binomialDistribution0 = null;
      try {
        binomialDistribution0 = new BinomialDistribution(1977, 1977);
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // 1,977 out of [0, 1] range
         //
         verifyException("org.apache.commons.math3.distribution.BinomialDistribution", e);
      }
  }

  @Test(timeout = 4000)
  public void test17()  throws Throwable  {
      Well19937c well19937c0 = new Well19937c();
      BinomialDistribution binomialDistribution0 = null;
      try {
        binomialDistribution0 = new BinomialDistribution(well19937c0, (-2567), 7.494218049456063E304);
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // number of trials (-2,567)
         //
         verifyException("org.apache.commons.math3.distribution.BinomialDistribution", e);
      }
  }

  @Test(timeout = 4000)
  public void test18()  throws Throwable  {
      BinomialDistribution binomialDistribution0 = new BinomialDistribution(1, 1.0);
      assertEquals(1.0, binomialDistribution0.getNumericalMean(), 0.01);
  }

  @Test(timeout = 4000)
  public void test19()  throws Throwable  {
      BinomialDistribution binomialDistribution0 = new BinomialDistribution((RandomGenerator) null, 0, 0);
      int int0 = binomialDistribution0.inverseCumulativeProbability(0);
      binomialDistribution0.inverseCumulativeProbability(0.0);
      binomialDistribution0.getNumericalMean();
      binomialDistribution0.getNumericalMean();
      int int1 = binomialDistribution0.getSupportUpperBound();
      assertTrue(int1 == int0);
      
      boolean boolean0 = binomialDistribution0.isSupportConnected();
      assertTrue(boolean0);
      
      double double0 = binomialDistribution0.logProbability(0);
      assertEquals(0.0, double0, 0.01);
      
      double double1 = binomialDistribution0.probability(1511);
      assertEquals(double1, double0, 0.01);
      
      double double2 = binomialDistribution0.getNumericalMean();
      assertEquals(0.0, double2, 0.01);
  }

  @Test(timeout = 4000)
  public void test20()  throws Throwable  {
      BinomialDistribution binomialDistribution0 = new BinomialDistribution((RandomGenerator) null, 0, 0);
      double double0 = binomialDistribution0.cumulativeProbability((-518));
      assertEquals(0.0, double0, 0.01);
      assertEquals(0, binomialDistribution0.getNumberOfTrials());
      assertEquals(0.0, binomialDistribution0.getNumericalMean(), 0.01);
  }

  @Test(timeout = 4000)
  public void test21()  throws Throwable  {
      BinomialDistribution binomialDistribution0 = null;
      try {
        binomialDistribution0 = new BinomialDistribution(1916, 1916);
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // 1,916 out of [0, 1] range
         //
         verifyException("org.apache.commons.math3.distribution.BinomialDistribution", e);
      }
  }

  @Test(timeout = 4000)
  public void test22()  throws Throwable  {
      BinomialDistribution binomialDistribution0 = new BinomialDistribution(1803, 0.0);
      double double0 = binomialDistribution0.cumulativeProbability(1803);
      assertEquals(1.0, double0, 0.01);
      
      binomialDistribution0.isSupportConnected();
      binomialDistribution0.solveInverseCumulativeProbability(1803, 1803, 1803);
      assertEquals(0, binomialDistribution0.getSupportUpperBound());
      
      binomialDistribution0.sample(1803);
      binomialDistribution0.solveInverseCumulativeProbability(1803, 1803, 1803);
      double double1 = binomialDistribution0.probability(0);
      double double2 = binomialDistribution0.probability(2793);
      binomialDistribution0.logProbability((-1938));
      double double3 = binomialDistribution0.cumulativeProbability(0);
      assertEquals(double3, double1, 0.01);
      
      binomialDistribution0.probability((-1938));
      double double4 = binomialDistribution0.cumulativeProbability(1803, 3285);
      assertEquals(0.0, double4, 0.01);
      
      binomialDistribution0.getNumericalVariance();
      int int0 = binomialDistribution0.getSupportLowerBound();
      assertEquals(0, int0);
      
      binomialDistribution0.isSupportConnected();
      double double5 = binomialDistribution0.getProbabilityOfSuccess();
      assertEquals(0.0, double5, 0.01);
      
      binomialDistribution0.probability((-1695));
      int int1 = binomialDistribution0.getNumberOfTrials();
      assertEquals(1803, int1);
      
      double double6 = binomialDistribution0.getNumericalMean();
      assertEquals(0.0, double6, 0.01);
      
      binomialDistribution0.getSupportUpperBound();
      double double7 = binomialDistribution0.getNumericalVariance();
      assertEquals(double7, double2, 0.01);
      assertEquals(0.0, double7, 0.01);
  }

  @Test(timeout = 4000)
  public void test23()  throws Throwable  {
      Well19937c well19937c0 = new Well19937c(804L);
      SynchronizedRandomGenerator synchronizedRandomGenerator0 = new SynchronizedRandomGenerator(well19937c0);
      int int0 = 6;
      synchronizedRandomGenerator0.setSeed((long) 6);
      BinomialDistribution binomialDistribution0 = null;
      try {
        binomialDistribution0 = new BinomialDistribution(synchronizedRandomGenerator0, 6, (-815.9708409723788));
        fail("Expecting exception: IllegalArgumentException");
      
      } catch(IllegalArgumentException e) {
         //
         // -815.971 out of [0, 1] range
         //
         verifyException("org.apache.commons.math3.distribution.BinomialDistribution", e);
      }
  }

  @Test(timeout = 4000)
  public void test24()  throws Throwable  {
      BinomialDistribution binomialDistribution0 = new BinomialDistribution(1, 1);
      binomialDistribution0.reseedRandomGenerator((-3132L));
      double double0 = binomialDistribution0.cumulativeProbability(1);
      double double1 = binomialDistribution0.getProbabilityOfSuccess();
      assertEquals(double1, double0, 0.01);
      
      binomialDistribution0.sample();
      double double2 = binomialDistribution0.logProbability(1);
      assertEquals(1.0, binomialDistribution0.getNumericalMean(), 0.01);
      assertEquals(-0.0, double2, 0.01);
      assertEquals(0.0, binomialDistribution0.getNumericalVariance(), 0.01);
      assertEquals(1, binomialDistribution0.getSupportLowerBound());
      assertEquals(1, binomialDistribution0.getSupportUpperBound());
  }
}