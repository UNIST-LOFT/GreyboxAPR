/*
 * This file was automatically generated by EvoSuite
 * Fri Dec 27 20:11:26 GMT 2019
 */

package org.apache.commons.math.ode.nonstiff;

import org.junit.Test;
import static org.junit.Assert.*;
import static org.evosuite.shaded.org.mockito.Mockito.*;
import static org.evosuite.runtime.EvoAssertions.*;
import org.apache.commons.math.ode.FirstOrderConverter;
import org.apache.commons.math.ode.FirstOrderDifferentialEquations;
import org.apache.commons.math.ode.SecondOrderDifferentialEquations;
import org.apache.commons.math.ode.events.EventHandler;
import org.apache.commons.math.ode.nonstiff.DormandPrince54Integrator;
import org.apache.commons.math.ode.nonstiff.DormandPrince853Integrator;
import org.apache.commons.math.ode.nonstiff.HighamHall54Integrator;
import org.evosuite.runtime.EvoRunner;
import org.evosuite.runtime.EvoRunnerParameters;
import org.evosuite.runtime.ViolatedAssumptionAnswer;
import org.junit.runner.RunWith;

@RunWith(EvoRunner.class) @EvoRunnerParameters(mockJVMNonDeterminism = true, useVFS = true, useVNET = true, resetStaticState = true, separateClassLoader = true, useJEE = true) 
public class EmbeddedRungeKuttaIntegrator_ESTest extends EmbeddedRungeKuttaIntegrator_ESTest_scaffolding {

  @Test(timeout = 4000)
  public void test00()  throws Throwable  {
      DormandPrince853Integrator dormandPrince853Integrator0 = new DormandPrince853Integrator(1.0, 1.0, 569.6, 569.6);
      assertEquals(10.0, dormandPrince853Integrator0.getMaxGrowth(), 0.01);
      assertEquals(0, dormandPrince853Integrator0.getEvaluations());
      assertEquals(1.0, dormandPrince853Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals(1.0, dormandPrince853Integrator0.getMaxStep(), 0.01);
      assertEquals(8, dormandPrince853Integrator0.getOrder());
      assertEquals(0.2, dormandPrince853Integrator0.getMinReduction(), 0.01);
      assertEquals(Double.NaN, dormandPrince853Integrator0.getCurrentStepStart(), 0.01);
      assertEquals(0.9, dormandPrince853Integrator0.getSafety(), 0.01);
      assertEquals(Integer.MAX_VALUE, dormandPrince853Integrator0.getMaxEvaluations());
      assertEquals("Dormand-Prince 8 (5, 3)", dormandPrince853Integrator0.getName());
      assertEquals(1.0, dormandPrince853Integrator0.getMinStep(), 0.01);
      assertNotNull(dormandPrince853Integrator0);
      
      SecondOrderDifferentialEquations secondOrderDifferentialEquations0 = mock(SecondOrderDifferentialEquations.class, new ViolatedAssumptionAnswer());
      doReturn(0).when(secondOrderDifferentialEquations0).getDimension();
      FirstOrderConverter firstOrderConverter0 = new FirstOrderConverter(secondOrderDifferentialEquations0);
      assertEquals(0, firstOrderConverter0.getDimension());
      assertNotNull(firstOrderConverter0);
      
      double[] doubleArray0 = new double[3];
      double[] doubleArray1 = new double[4];
      assertFalse(doubleArray1.equals((Object)doubleArray0));
      
      try { 
        dormandPrince853Integrator0.integrate(firstOrderConverter0, 569.6, doubleArray0, 0.375, doubleArray1);
        fail("Expecting exception: Exception");
      
      } catch(Exception e) {
         //
         // dimensions mismatch: ODE problem has dimension 0, initial state vector has dimension 3
         //
         verifyException("org.apache.commons.math.ode.AbstractIntegrator", e);
      }
  }

  @Test(timeout = 4000)
  public void test01()  throws Throwable  {
      HighamHall54Integrator highamHall54Integrator0 = new HighamHall54Integrator(0.0, 0.0, 0.0, 0.0);
      assertEquals(0.2, highamHall54Integrator0.getMinReduction(), 0.01);
      assertEquals(0.9, highamHall54Integrator0.getSafety(), 0.01);
      assertEquals(10.0, highamHall54Integrator0.getMaxGrowth(), 0.01);
      assertEquals(0.0, highamHall54Integrator0.getMinStep(), 0.01);
      assertEquals(0.0, highamHall54Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals(0.0, highamHall54Integrator0.getMaxStep(), 0.01);
      assertEquals(5, highamHall54Integrator0.getOrder());
      assertEquals(0, highamHall54Integrator0.getEvaluations());
      assertEquals(Integer.MAX_VALUE, highamHall54Integrator0.getMaxEvaluations());
      assertEquals("Higham-Hall 5(4)", highamHall54Integrator0.getName());
      assertEquals(Double.NaN, highamHall54Integrator0.getCurrentStepStart(), 0.01);
      assertNotNull(highamHall54Integrator0);
      
      highamHall54Integrator0.setSafety(0.0);
      assertEquals(0.0, highamHall54Integrator0.getSafety(), 0.01);
      assertEquals(0.2, highamHall54Integrator0.getMinReduction(), 0.01);
      assertEquals(10.0, highamHall54Integrator0.getMaxGrowth(), 0.01);
      assertEquals(0.0, highamHall54Integrator0.getMinStep(), 0.01);
      assertEquals(0.0, highamHall54Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals(0.0, highamHall54Integrator0.getMaxStep(), 0.01);
      assertEquals(5, highamHall54Integrator0.getOrder());
      assertEquals(0, highamHall54Integrator0.getEvaluations());
      assertEquals(Integer.MAX_VALUE, highamHall54Integrator0.getMaxEvaluations());
      assertEquals("Higham-Hall 5(4)", highamHall54Integrator0.getName());
      assertEquals(Double.NaN, highamHall54Integrator0.getCurrentStepStart(), 0.01);
      
      double double0 = highamHall54Integrator0.getSafety();
      assertEquals(0.0, highamHall54Integrator0.getSafety(), 0.01);
      assertEquals(0.2, highamHall54Integrator0.getMinReduction(), 0.01);
      assertEquals(10.0, highamHall54Integrator0.getMaxGrowth(), 0.01);
      assertEquals(0.0, highamHall54Integrator0.getMinStep(), 0.01);
      assertEquals(0.0, highamHall54Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals(0.0, highamHall54Integrator0.getMaxStep(), 0.01);
      assertEquals(5, highamHall54Integrator0.getOrder());
      assertEquals(0, highamHall54Integrator0.getEvaluations());
      assertEquals(Integer.MAX_VALUE, highamHall54Integrator0.getMaxEvaluations());
      assertEquals("Higham-Hall 5(4)", highamHall54Integrator0.getName());
      assertEquals(Double.NaN, highamHall54Integrator0.getCurrentStepStart(), 0.01);
      assertEquals(0.0, double0, 0.01);
  }

  @Test(timeout = 4000)
  public void test02()  throws Throwable  {
      DormandPrince54Integrator dormandPrince54Integrator0 = new DormandPrince54Integrator(0.0, 0.0, 0.0, 0.0);
      assertEquals(Double.NaN, dormandPrince54Integrator0.getCurrentStepStart(), 0.01);
      assertEquals(0.0, dormandPrince54Integrator0.getMaxStep(), 0.01);
      assertEquals(0.9, dormandPrince54Integrator0.getSafety(), 0.01);
      assertEquals(5, dormandPrince54Integrator0.getOrder());
      assertEquals(0.2, dormandPrince54Integrator0.getMinReduction(), 0.01);
      assertEquals(0.0, dormandPrince54Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals(10.0, dormandPrince54Integrator0.getMaxGrowth(), 0.01);
      assertEquals(0.0, dormandPrince54Integrator0.getMinStep(), 0.01);
      assertEquals("Dormand-Prince 5(4)", dormandPrince54Integrator0.getName());
      assertEquals(0, dormandPrince54Integrator0.getEvaluations());
      assertEquals(Integer.MAX_VALUE, dormandPrince54Integrator0.getMaxEvaluations());
      assertNotNull(dormandPrince54Integrator0);
      
      dormandPrince54Integrator0.setSafety((-1643.2807356998685));
      assertEquals(Double.NaN, dormandPrince54Integrator0.getCurrentStepStart(), 0.01);
      assertEquals((-1643.2807356998685), dormandPrince54Integrator0.getSafety(), 0.01);
      assertEquals(0.0, dormandPrince54Integrator0.getMaxStep(), 0.01);
      assertEquals(5, dormandPrince54Integrator0.getOrder());
      assertEquals(0.2, dormandPrince54Integrator0.getMinReduction(), 0.01);
      assertEquals(0.0, dormandPrince54Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals(10.0, dormandPrince54Integrator0.getMaxGrowth(), 0.01);
      assertEquals(0.0, dormandPrince54Integrator0.getMinStep(), 0.01);
      assertEquals("Dormand-Prince 5(4)", dormandPrince54Integrator0.getName());
      assertEquals(0, dormandPrince54Integrator0.getEvaluations());
      assertEquals(Integer.MAX_VALUE, dormandPrince54Integrator0.getMaxEvaluations());
      
      double double0 = dormandPrince54Integrator0.getSafety();
      assertEquals(Double.NaN, dormandPrince54Integrator0.getCurrentStepStart(), 0.01);
      assertEquals((-1643.2807356998685), dormandPrince54Integrator0.getSafety(), 0.01);
      assertEquals(0.0, dormandPrince54Integrator0.getMaxStep(), 0.01);
      assertEquals(5, dormandPrince54Integrator0.getOrder());
      assertEquals(0.2, dormandPrince54Integrator0.getMinReduction(), 0.01);
      assertEquals(0.0, dormandPrince54Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals(10.0, dormandPrince54Integrator0.getMaxGrowth(), 0.01);
      assertEquals(0.0, dormandPrince54Integrator0.getMinStep(), 0.01);
      assertEquals("Dormand-Prince 5(4)", dormandPrince54Integrator0.getName());
      assertEquals(0, dormandPrince54Integrator0.getEvaluations());
      assertEquals(Integer.MAX_VALUE, dormandPrince54Integrator0.getMaxEvaluations());
      assertEquals((-1643.2807356998685), double0, 0.01);
  }

  @Test(timeout = 4000)
  public void test03()  throws Throwable  {
      HighamHall54Integrator highamHall54Integrator0 = new HighamHall54Integrator((-741.4), 1987.307291, 1987.307291, 18.148505520854727);
      assertEquals(10.0, highamHall54Integrator0.getMaxGrowth(), 0.01);
      assertEquals(741.4, highamHall54Integrator0.getMinStep(), 0.01);
      assertEquals(Integer.MAX_VALUE, highamHall54Integrator0.getMaxEvaluations());
      assertEquals(0, highamHall54Integrator0.getEvaluations());
      assertEquals("Higham-Hall 5(4)", highamHall54Integrator0.getName());
      assertEquals(1213.8326184229027, highamHall54Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals(Double.NaN, highamHall54Integrator0.getCurrentStepStart(), 0.01);
      assertEquals(1987.307291, highamHall54Integrator0.getMaxStep(), 0.01);
      assertEquals(0.2, highamHall54Integrator0.getMinReduction(), 0.01);
      assertEquals(0.9, highamHall54Integrator0.getSafety(), 0.01);
      assertEquals(5, highamHall54Integrator0.getOrder());
      assertNotNull(highamHall54Integrator0);
      
      int int0 = highamHall54Integrator0.getOrder();
      assertEquals(10.0, highamHall54Integrator0.getMaxGrowth(), 0.01);
      assertEquals(741.4, highamHall54Integrator0.getMinStep(), 0.01);
      assertEquals(Integer.MAX_VALUE, highamHall54Integrator0.getMaxEvaluations());
      assertEquals(0, highamHall54Integrator0.getEvaluations());
      assertEquals("Higham-Hall 5(4)", highamHall54Integrator0.getName());
      assertEquals(1213.8326184229027, highamHall54Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals(Double.NaN, highamHall54Integrator0.getCurrentStepStart(), 0.01);
      assertEquals(1987.307291, highamHall54Integrator0.getMaxStep(), 0.01);
      assertEquals(0.2, highamHall54Integrator0.getMinReduction(), 0.01);
      assertEquals(0.9, highamHall54Integrator0.getSafety(), 0.01);
      assertEquals(5, highamHall54Integrator0.getOrder());
      assertEquals(5, int0);
  }

  @Test(timeout = 4000)
  public void test04()  throws Throwable  {
      DormandPrince54Integrator dormandPrince54Integrator0 = new DormandPrince54Integrator(0.0, (-3450.757), (-3450.757), 0.0);
      assertEquals(3450.757, dormandPrince54Integrator0.getMaxStep(), 0.01);
      assertEquals(5, dormandPrince54Integrator0.getOrder());
      assertEquals(0.9, dormandPrince54Integrator0.getSafety(), 0.01);
      assertEquals(10.0, dormandPrince54Integrator0.getMaxGrowth(), 0.01);
      assertEquals(0.2, dormandPrince54Integrator0.getMinReduction(), 0.01);
      assertEquals(0.0, dormandPrince54Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals(Double.NaN, dormandPrince54Integrator0.getCurrentStepStart(), 0.01);
      assertEquals(0, dormandPrince54Integrator0.getEvaluations());
      assertEquals(Integer.MAX_VALUE, dormandPrince54Integrator0.getMaxEvaluations());
      assertEquals("Dormand-Prince 5(4)", dormandPrince54Integrator0.getName());
      assertEquals(0.0, dormandPrince54Integrator0.getMinStep(), 0.01);
      assertNotNull(dormandPrince54Integrator0);
      
      dormandPrince54Integrator0.setMinReduction(0.0);
      assertEquals(3450.757, dormandPrince54Integrator0.getMaxStep(), 0.01);
      assertEquals(5, dormandPrince54Integrator0.getOrder());
      assertEquals(0.9, dormandPrince54Integrator0.getSafety(), 0.01);
      assertEquals(10.0, dormandPrince54Integrator0.getMaxGrowth(), 0.01);
      assertEquals(0.0, dormandPrince54Integrator0.getMinReduction(), 0.01);
      assertEquals(0.0, dormandPrince54Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals(Double.NaN, dormandPrince54Integrator0.getCurrentStepStart(), 0.01);
      assertEquals(0, dormandPrince54Integrator0.getEvaluations());
      assertEquals(Integer.MAX_VALUE, dormandPrince54Integrator0.getMaxEvaluations());
      assertEquals("Dormand-Prince 5(4)", dormandPrince54Integrator0.getName());
      assertEquals(0.0, dormandPrince54Integrator0.getMinStep(), 0.01);
      
      double double0 = dormandPrince54Integrator0.getMinReduction();
      assertEquals(3450.757, dormandPrince54Integrator0.getMaxStep(), 0.01);
      assertEquals(5, dormandPrince54Integrator0.getOrder());
      assertEquals(0.9, dormandPrince54Integrator0.getSafety(), 0.01);
      assertEquals(10.0, dormandPrince54Integrator0.getMaxGrowth(), 0.01);
      assertEquals(0.0, dormandPrince54Integrator0.getMinReduction(), 0.01);
      assertEquals(0.0, dormandPrince54Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals(Double.NaN, dormandPrince54Integrator0.getCurrentStepStart(), 0.01);
      assertEquals(0, dormandPrince54Integrator0.getEvaluations());
      assertEquals(Integer.MAX_VALUE, dormandPrince54Integrator0.getMaxEvaluations());
      assertEquals("Dormand-Prince 5(4)", dormandPrince54Integrator0.getName());
      assertEquals(0.0, dormandPrince54Integrator0.getMinStep(), 0.01);
      assertEquals(0.0, double0, 0.01);
  }

  @Test(timeout = 4000)
  public void test05()  throws Throwable  {
      DormandPrince54Integrator dormandPrince54Integrator0 = new DormandPrince54Integrator(0.0, (-3450.757), (-3450.757), (-3450.757));
      assertEquals(0.9, dormandPrince54Integrator0.getSafety(), 0.01);
      assertEquals(0.2, dormandPrince54Integrator0.getMinReduction(), 0.01);
      assertEquals(5, dormandPrince54Integrator0.getOrder());
      assertEquals(3450.757, dormandPrince54Integrator0.getMaxStep(), 0.01);
      assertEquals(0.0, dormandPrince54Integrator0.getMinStep(), 0.01);
      assertEquals(10.0, dormandPrince54Integrator0.getMaxGrowth(), 0.01);
      assertEquals("Dormand-Prince 5(4)", dormandPrince54Integrator0.getName());
      assertEquals(0.0, dormandPrince54Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals(Integer.MAX_VALUE, dormandPrince54Integrator0.getMaxEvaluations());
      assertEquals(Double.NaN, dormandPrince54Integrator0.getCurrentStepStart(), 0.01);
      assertEquals(0, dormandPrince54Integrator0.getEvaluations());
      assertNotNull(dormandPrince54Integrator0);
      
      dormandPrince54Integrator0.setMinReduction((-3450.757));
      assertEquals(0.9, dormandPrince54Integrator0.getSafety(), 0.01);
      assertEquals(5, dormandPrince54Integrator0.getOrder());
      assertEquals(3450.757, dormandPrince54Integrator0.getMaxStep(), 0.01);
      assertEquals((-3450.757), dormandPrince54Integrator0.getMinReduction(), 0.01);
      assertEquals(0.0, dormandPrince54Integrator0.getMinStep(), 0.01);
      assertEquals(10.0, dormandPrince54Integrator0.getMaxGrowth(), 0.01);
      assertEquals("Dormand-Prince 5(4)", dormandPrince54Integrator0.getName());
      assertEquals(0.0, dormandPrince54Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals(Integer.MAX_VALUE, dormandPrince54Integrator0.getMaxEvaluations());
      assertEquals(Double.NaN, dormandPrince54Integrator0.getCurrentStepStart(), 0.01);
      assertEquals(0, dormandPrince54Integrator0.getEvaluations());
      
      double double0 = dormandPrince54Integrator0.getMinReduction();
      assertEquals(0.9, dormandPrince54Integrator0.getSafety(), 0.01);
      assertEquals(5, dormandPrince54Integrator0.getOrder());
      assertEquals(3450.757, dormandPrince54Integrator0.getMaxStep(), 0.01);
      assertEquals((-3450.757), dormandPrince54Integrator0.getMinReduction(), 0.01);
      assertEquals(0.0, dormandPrince54Integrator0.getMinStep(), 0.01);
      assertEquals(10.0, dormandPrince54Integrator0.getMaxGrowth(), 0.01);
      assertEquals("Dormand-Prince 5(4)", dormandPrince54Integrator0.getName());
      assertEquals(0.0, dormandPrince54Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals(Integer.MAX_VALUE, dormandPrince54Integrator0.getMaxEvaluations());
      assertEquals(Double.NaN, dormandPrince54Integrator0.getCurrentStepStart(), 0.01);
      assertEquals(0, dormandPrince54Integrator0.getEvaluations());
      assertEquals((-3450.757), double0, 0.01);
  }

  @Test(timeout = 4000)
  public void test06()  throws Throwable  {
      DormandPrince54Integrator dormandPrince54Integrator0 = new DormandPrince54Integrator(1.0, 0.0, (-988.94338306091), 0.0);
      assertEquals(Integer.MAX_VALUE, dormandPrince54Integrator0.getMaxEvaluations());
      assertEquals(0.0, dormandPrince54Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals(1.0, dormandPrince54Integrator0.getMinStep(), 0.01);
      assertEquals(10.0, dormandPrince54Integrator0.getMaxGrowth(), 0.01);
      assertEquals(5, dormandPrince54Integrator0.getOrder());
      assertEquals("Dormand-Prince 5(4)", dormandPrince54Integrator0.getName());
      assertEquals(0.2, dormandPrince54Integrator0.getMinReduction(), 0.01);
      assertEquals(0.9, dormandPrince54Integrator0.getSafety(), 0.01);
      assertEquals(Double.NaN, dormandPrince54Integrator0.getCurrentStepStart(), 0.01);
      assertEquals(0, dormandPrince54Integrator0.getEvaluations());
      assertEquals(0.0, dormandPrince54Integrator0.getMaxStep(), 0.01);
      assertNotNull(dormandPrince54Integrator0);
      
      dormandPrince54Integrator0.setMaxGrowth(0.0);
      assertEquals(0.0, dormandPrince54Integrator0.getMaxGrowth(), 0.01);
      assertEquals(Integer.MAX_VALUE, dormandPrince54Integrator0.getMaxEvaluations());
      assertEquals(0.0, dormandPrince54Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals(1.0, dormandPrince54Integrator0.getMinStep(), 0.01);
      assertEquals(5, dormandPrince54Integrator0.getOrder());
      assertEquals("Dormand-Prince 5(4)", dormandPrince54Integrator0.getName());
      assertEquals(0.2, dormandPrince54Integrator0.getMinReduction(), 0.01);
      assertEquals(0.9, dormandPrince54Integrator0.getSafety(), 0.01);
      assertEquals(Double.NaN, dormandPrince54Integrator0.getCurrentStepStart(), 0.01);
      assertEquals(0, dormandPrince54Integrator0.getEvaluations());
      assertEquals(0.0, dormandPrince54Integrator0.getMaxStep(), 0.01);
      
      double double0 = dormandPrince54Integrator0.getMaxGrowth();
      assertEquals(0.0, dormandPrince54Integrator0.getMaxGrowth(), 0.01);
      assertEquals(Integer.MAX_VALUE, dormandPrince54Integrator0.getMaxEvaluations());
      assertEquals(0.0, dormandPrince54Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals(1.0, dormandPrince54Integrator0.getMinStep(), 0.01);
      assertEquals(5, dormandPrince54Integrator0.getOrder());
      assertEquals("Dormand-Prince 5(4)", dormandPrince54Integrator0.getName());
      assertEquals(0.2, dormandPrince54Integrator0.getMinReduction(), 0.01);
      assertEquals(0.9, dormandPrince54Integrator0.getSafety(), 0.01);
      assertEquals(Double.NaN, dormandPrince54Integrator0.getCurrentStepStart(), 0.01);
      assertEquals(0, dormandPrince54Integrator0.getEvaluations());
      assertEquals(0.0, dormandPrince54Integrator0.getMaxStep(), 0.01);
      assertEquals(0.0, double0, 0.01);
  }

  @Test(timeout = 4000)
  public void test07()  throws Throwable  {
      DormandPrince54Integrator dormandPrince54Integrator0 = new DormandPrince54Integrator(2109.4, 6.813832283771934, 2109.4, 2109.4);
      assertEquals(6.813832283771934, dormandPrince54Integrator0.getMaxStep(), 0.01);
      assertEquals(0.9, dormandPrince54Integrator0.getSafety(), 0.01);
      assertEquals(5, dormandPrince54Integrator0.getOrder());
      assertEquals(0.2, dormandPrince54Integrator0.getMinReduction(), 0.01);
      assertEquals(2109.4, dormandPrince54Integrator0.getMinStep(), 0.01);
      assertEquals(Double.NaN, dormandPrince54Integrator0.getCurrentStepStart(), 0.01);
      assertEquals(0, dormandPrince54Integrator0.getEvaluations());
      assertEquals(Integer.MAX_VALUE, dormandPrince54Integrator0.getMaxEvaluations());
      assertEquals(10.0, dormandPrince54Integrator0.getMaxGrowth(), 0.01);
      assertEquals("Dormand-Prince 5(4)", dormandPrince54Integrator0.getName());
      assertEquals(119.88785517886504, dormandPrince54Integrator0.getCurrentSignedStepsize(), 0.01);
      assertNotNull(dormandPrince54Integrator0);
      
      dormandPrince54Integrator0.setMaxGrowth((-298.757277));
      assertEquals((-298.757277), dormandPrince54Integrator0.getMaxGrowth(), 0.01);
      assertEquals(6.813832283771934, dormandPrince54Integrator0.getMaxStep(), 0.01);
      assertEquals(0.9, dormandPrince54Integrator0.getSafety(), 0.01);
      assertEquals(5, dormandPrince54Integrator0.getOrder());
      assertEquals(0.2, dormandPrince54Integrator0.getMinReduction(), 0.01);
      assertEquals(2109.4, dormandPrince54Integrator0.getMinStep(), 0.01);
      assertEquals(Double.NaN, dormandPrince54Integrator0.getCurrentStepStart(), 0.01);
      assertEquals(0, dormandPrince54Integrator0.getEvaluations());
      assertEquals(Integer.MAX_VALUE, dormandPrince54Integrator0.getMaxEvaluations());
      assertEquals("Dormand-Prince 5(4)", dormandPrince54Integrator0.getName());
      assertEquals(119.88785517886504, dormandPrince54Integrator0.getCurrentSignedStepsize(), 0.01);
      
      double double0 = dormandPrince54Integrator0.getMaxGrowth();
      assertEquals((-298.757277), dormandPrince54Integrator0.getMaxGrowth(), 0.01);
      assertEquals(6.813832283771934, dormandPrince54Integrator0.getMaxStep(), 0.01);
      assertEquals(0.9, dormandPrince54Integrator0.getSafety(), 0.01);
      assertEquals(5, dormandPrince54Integrator0.getOrder());
      assertEquals(0.2, dormandPrince54Integrator0.getMinReduction(), 0.01);
      assertEquals(2109.4, dormandPrince54Integrator0.getMinStep(), 0.01);
      assertEquals(Double.NaN, dormandPrince54Integrator0.getCurrentStepStart(), 0.01);
      assertEquals(0, dormandPrince54Integrator0.getEvaluations());
      assertEquals(Integer.MAX_VALUE, dormandPrince54Integrator0.getMaxEvaluations());
      assertEquals("Dormand-Prince 5(4)", dormandPrince54Integrator0.getName());
      assertEquals(119.88785517886504, dormandPrince54Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals((-298.757277), double0, 0.01);
  }

  @Test(timeout = 4000)
  public void test08()  throws Throwable  {
      HighamHall54Integrator highamHall54Integrator0 = new HighamHall54Integrator(0.0, 0.0, 0.0, 0.0);
      assertEquals(Double.NaN, highamHall54Integrator0.getCurrentStepStart(), 0.01);
      assertEquals(0.0, highamHall54Integrator0.getMaxStep(), 0.01);
      assertEquals(5, highamHall54Integrator0.getOrder());
      assertEquals(0.0, highamHall54Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals(0.9, highamHall54Integrator0.getSafety(), 0.01);
      assertEquals(0.2, highamHall54Integrator0.getMinReduction(), 0.01);
      assertEquals("Higham-Hall 5(4)", highamHall54Integrator0.getName());
      assertEquals(10.0, highamHall54Integrator0.getMaxGrowth(), 0.01);
      assertEquals(0, highamHall54Integrator0.getEvaluations());
      assertEquals(Integer.MAX_VALUE, highamHall54Integrator0.getMaxEvaluations());
      assertEquals(0.0, highamHall54Integrator0.getMinStep(), 0.01);
      assertNotNull(highamHall54Integrator0);
      
      double[] doubleArray0 = new double[3];
      // Undeclared exception!
      try { 
        highamHall54Integrator0.integrate((FirstOrderDifferentialEquations) null, 1535.9021080435, doubleArray0, 2686.39422837, doubleArray0);
        fail("Expecting exception: NullPointerException");
      
      } catch(NullPointerException e) {
         //
         // no message in exception (getMessage() returned null)
         //
         verifyException("org.apache.commons.math.ode.AbstractIntegrator", e);
      }
  }

  @Test(timeout = 4000)
  public void test09()  throws Throwable  {
      double[] doubleArray0 = new double[6];
      DormandPrince54Integrator dormandPrince54Integrator0 = new DormandPrince54Integrator(3094.07541125, 2142.0, doubleArray0, doubleArray0);
      assertEquals(2142.0, dormandPrince54Integrator0.getMaxStep(), 0.01);
      assertEquals(0.2, dormandPrince54Integrator0.getMinReduction(), 0.01);
      assertEquals("Dormand-Prince 5(4)", dormandPrince54Integrator0.getName());
      assertEquals(3094.07541125, dormandPrince54Integrator0.getMinStep(), 0.01);
      assertEquals(0.9, dormandPrince54Integrator0.getSafety(), 0.01);
      assertEquals(10.0, dormandPrince54Integrator0.getMaxGrowth(), 0.01);
      assertEquals(5, dormandPrince54Integrator0.getOrder());
      assertEquals(Double.NaN, dormandPrince54Integrator0.getCurrentStepStart(), 0.01);
      assertEquals(2574.3949834665036, dormandPrince54Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals(0, dormandPrince54Integrator0.getEvaluations());
      assertEquals(Integer.MAX_VALUE, dormandPrince54Integrator0.getMaxEvaluations());
      assertNotNull(dormandPrince54Integrator0);
      assertArrayEquals(new double[] {0.0, 0.0, 0.0, 0.0, 0.0, 0.0}, doubleArray0, 0.01);
      assertEquals(6, doubleArray0.length);
      
      SecondOrderDifferentialEquations secondOrderDifferentialEquations0 = mock(SecondOrderDifferentialEquations.class, new ViolatedAssumptionAnswer());
      doReturn(3).when(secondOrderDifferentialEquations0).getDimension();
      FirstOrderConverter firstOrderConverter0 = new FirstOrderConverter(secondOrderDifferentialEquations0);
      assertEquals(6, firstOrderConverter0.getDimension());
      assertNotNull(firstOrderConverter0);
      
      // Undeclared exception!
      dormandPrince54Integrator0.integrate(firstOrderConverter0, (-0.3333333333333333), doubleArray0, 0.2, doubleArray0);
  }

  @Test(timeout = 4000)
  public void test10()  throws Throwable  {
      DormandPrince54Integrator dormandPrince54Integrator0 = new DormandPrince54Integrator((-4002.4), 0.0, (-4002.4), 0.0);
      assertEquals(10.0, dormandPrince54Integrator0.getMaxGrowth(), 0.01);
      assertEquals("Dormand-Prince 5(4)", dormandPrince54Integrator0.getName());
      assertEquals(0, dormandPrince54Integrator0.getEvaluations());
      assertEquals(Integer.MAX_VALUE, dormandPrince54Integrator0.getMaxEvaluations());
      assertEquals(4002.4, dormandPrince54Integrator0.getMinStep(), 0.01);
      assertEquals(Double.NaN, dormandPrince54Integrator0.getCurrentStepStart(), 0.01);
      assertEquals(0.0, dormandPrince54Integrator0.getMaxStep(), 0.01);
      assertEquals(0.0, dormandPrince54Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals(0.9, dormandPrince54Integrator0.getSafety(), 0.01);
      assertEquals(0.2, dormandPrince54Integrator0.getMinReduction(), 0.01);
      assertEquals(5, dormandPrince54Integrator0.getOrder());
      assertNotNull(dormandPrince54Integrator0);
      
      SecondOrderDifferentialEquations secondOrderDifferentialEquations0 = mock(SecondOrderDifferentialEquations.class, new ViolatedAssumptionAnswer());
      doReturn(2).when(secondOrderDifferentialEquations0).getDimension();
      FirstOrderConverter firstOrderConverter0 = new FirstOrderConverter(secondOrderDifferentialEquations0);
      assertEquals(4, firstOrderConverter0.getDimension());
      assertNotNull(firstOrderConverter0);
      
      double[] doubleArray0 = new double[4];
      try { 
        dormandPrince54Integrator0.integrate(firstOrderConverter0, (-2268.2500786287524), doubleArray0, 2371.83, doubleArray0);
        fail("Expecting exception: Exception");
      
      } catch(Exception e) {
         //
         // minimal step size (4.00E03) reached, integration needs 0.00E00
         //
         verifyException("org.apache.commons.math.ode.nonstiff.AdaptiveStepsizeIntegrator", e);
      }
  }

  @Test(timeout = 4000)
  public void test11()  throws Throwable  {
      DormandPrince853Integrator dormandPrince853Integrator0 = new DormandPrince853Integrator(0.2, 0.2, 0.2, 0.2);
      assertEquals(10.0, dormandPrince853Integrator0.getMaxGrowth(), 0.01);
      assertEquals(0.2, dormandPrince853Integrator0.getMinStep(), 0.01);
      assertEquals(8, dormandPrince853Integrator0.getOrder());
      assertEquals(0.9, dormandPrince853Integrator0.getSafety(), 0.01);
      assertEquals("Dormand-Prince 8 (5, 3)", dormandPrince853Integrator0.getName());
      assertEquals(0.2, dormandPrince853Integrator0.getMaxStep(), 0.01);
      assertEquals(0.2, dormandPrince853Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals(0.2, dormandPrince853Integrator0.getMinReduction(), 0.01);
      assertEquals(0, dormandPrince853Integrator0.getEvaluations());
      assertEquals(Integer.MAX_VALUE, dormandPrince853Integrator0.getMaxEvaluations());
      assertEquals(Double.NaN, dormandPrince853Integrator0.getCurrentStepStart(), 0.01);
      assertNotNull(dormandPrince853Integrator0);
      
      double[] doubleArray0 = new double[0];
      SecondOrderDifferentialEquations secondOrderDifferentialEquations0 = mock(SecondOrderDifferentialEquations.class, new ViolatedAssumptionAnswer());
      doReturn(0).when(secondOrderDifferentialEquations0).getDimension();
      FirstOrderConverter firstOrderConverter0 = new FirstOrderConverter(secondOrderDifferentialEquations0);
      assertEquals(0, firstOrderConverter0.getDimension());
      assertNotNull(firstOrderConverter0);
      
      EventHandler eventHandler0 = mock(EventHandler.class, new ViolatedAssumptionAnswer());
      dormandPrince853Integrator0.addEventHandler(eventHandler0, 2519.03, 2471.8892722, 2238);
      assertEquals(10.0, dormandPrince853Integrator0.getMaxGrowth(), 0.01);
      assertEquals(0.2, dormandPrince853Integrator0.getMinStep(), 0.01);
      assertEquals(8, dormandPrince853Integrator0.getOrder());
      assertEquals(0.9, dormandPrince853Integrator0.getSafety(), 0.01);
      assertEquals("Dormand-Prince 8 (5, 3)", dormandPrince853Integrator0.getName());
      assertEquals(0.2, dormandPrince853Integrator0.getMaxStep(), 0.01);
      assertEquals(0.2, dormandPrince853Integrator0.getCurrentSignedStepsize(), 0.01);
      assertEquals(0.2, dormandPrince853Integrator0.getMinReduction(), 0.01);
      assertEquals(0, dormandPrince853Integrator0.getEvaluations());
      assertEquals(Integer.MAX_VALUE, dormandPrince853Integrator0.getMaxEvaluations());
      assertEquals(Double.NaN, dormandPrince853Integrator0.getCurrentStepStart(), 0.01);
      
      // Undeclared exception!
      dormandPrince853Integrator0.integrate(firstOrderConverter0, 4.0, doubleArray0, Double.NaN, doubleArray0);
  }

  @Test(timeout = 4000)
  public void test12()  throws Throwable  {
      HighamHall54Integrator highamHall54Integrator0 = new HighamHall54Integrator(3896.653, (-0.10416666666666667), (-2268.24389), 0.0);
      SecondOrderDifferentialEquations secondOrderDifferentialEquations0 = mock(SecondOrderDifferentialEquations.class, new ViolatedAssumptionAnswer());
      doReturn(0).when(secondOrderDifferentialEquations0).getDimension();
      FirstOrderConverter firstOrderConverter0 = new FirstOrderConverter(secondOrderDifferentialEquations0);
      double[] doubleArray0 = new double[0];
      // Undeclared exception!
      highamHall54Integrator0.integrate(firstOrderConverter0, 612.268929, doubleArray0, 0.8, doubleArray0);
  }

  @Test(timeout = 4000)
  public void test13()  throws Throwable  {
      DormandPrince54Integrator dormandPrince54Integrator0 = new DormandPrince54Integrator(0.6, 18.148505520854727, 0.6, 0.0);
      double double0 = dormandPrince54Integrator0.getMaxGrowth();
      assertEquals(0.9, dormandPrince54Integrator0.getSafety(), 0.01);
      assertEquals(10.0, double0, 0.01);
      assertEquals(0.2, dormandPrince54Integrator0.getMinReduction(), 0.01);
  }

  @Test(timeout = 4000)
  public void test14()  throws Throwable  {
      DormandPrince54Integrator dormandPrince54Integrator0 = new DormandPrince54Integrator(0.0, 0.0, 0.0, 0.0);
      double double0 = dormandPrince54Integrator0.getMinReduction();
      assertEquals(10.0, dormandPrince54Integrator0.getMaxGrowth(), 0.01);
      assertEquals(0.9, dormandPrince54Integrator0.getSafety(), 0.01);
      assertEquals(0.2, double0, 0.01);
  }

  @Test(timeout = 4000)
  public void test15()  throws Throwable  {
      DormandPrince54Integrator dormandPrince54Integrator0 = new DormandPrince54Integrator(0.0, 0.0, 0.0, 0.0);
      double double0 = dormandPrince54Integrator0.getSafety();
      assertEquals(0.9, double0, 0.01);
      assertEquals(0.2, dormandPrince54Integrator0.getMinReduction(), 0.01);
      assertEquals(10.0, dormandPrince54Integrator0.getMaxGrowth(), 0.01);
  }
}