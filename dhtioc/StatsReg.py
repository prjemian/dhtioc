#!/usr/bin/env python

'''Implement a set of statistics registers in the style of a pocket calculator.

The available routines are::

     def Clear():                        clear the stats registers
     def Show():                         print the contents of the stats registers
     def Add(x, y):                      add an X,Y pair
     def Subtract(x, y):                 remove an X,Y pair
     def AddWeighted(x, y, z):           add an X,Y pair with weight Z
     def SubtractWeighted(x, y, z):      remove an X,Y pair with weight Z
     def Mean():                         arithmetic mean of X & Y
     def StdDev():                       standard deviation on X & Y
     def StdErr():                       standard error on X & Y
     def LinearRegression():             linear regression
     def LinearRegressionVariance():     est. errors of slope & intercept
     def LinearRegressionCorrelation():  the regression coefficient
     def CorrelationCoefficient():       relation of errors in slope & intercept

:see: http://stattrek.com/AP-Statistics-1/Regression.aspx?Tutorial=Stat

pocket calculator Statistical Registers, Pete Jemian, 2003-Apr-18

Source code documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
'''



import math
import os
import sys


version = '0.1a'


class StatsRegClass:
    """pocket calculator Statistical Registers class"""

    def __init__(self):
        """Set up the statistics registers."""
        self.Clear()

    def _ClearResults_(self):
        '''
        Cache the results to avoid unnecessary recalculation.
        When requested, test for None before recalculating.
        '''
        self.slope = None
        self.intercept = None
        self.determ = None
        self.mean = None
        self.sDev = None
        self.sErr = None
        self.lrVariance = None
        self.r = None
        self.correlation = None

    def Clear(self):
        '''
        clear the statistics registers:
        :math:`N=w=\sum{x}=\sum{x^2}=\sum{y}=\sum{y^2}=\sum{xy}=0`
        '''
        self.count = 0
        self.weight = 0
        self.sumX   = 0
        self.sumXX  = 0
        self.sumY   = 0
        self.sumYY  = 0
        self.sumXY  = 0
        self._ClearResults_()

    def Show(self):
        """contents of the statistics registers"""
        print(self.Show.__doc__)
        print("\t%s=%d"        % ('NumPts',   self.count))
        print("\t%s=%g\t%s=%g" % ('SumX  ',   self.sumX,   'SumXX',   self.sumXX))
        print("\t%s=%g\t%s=%g" % ('SumY  ',   self.sumY,   'SumYY',   self.sumYY))
        print("\t%s=%g\t%s=%g" % ('weight',   self.weight, 'SumXY',   self.sumXY))

    def Add(self, x, y):
        '''
        add an X,Y pair to the statistics registers

        :param float x: value to accumulate
        :param float y: value to accumulate
        '''
        return self.AddWeighted(x,y, 1)

    def Subtract(self, x, y):
        '''
        remove an X,Y pair from the statistics registers

        :param float x: value to remove
        :param float y: value to remove
        '''
        return self.SubtractWeighted(x,y, 1)

    def AddWeighted(self, x, y, z):
        '''
        add a weighted X,Y, +/- Z trio to the statistics registers

        :param float x: value to accumulate
        :param float y: value to accumulate
        :param float z: variance (weight = ``1/z^2``) of y
        '''
        self._ClearResults_()
        # TODO: verify handling of weight
        weight = 1.0/(z**2)
        xWt = x*weight
        yWt = y*weight
        self.count  += 1
        self.weight += weight
        self.sumX   += xWt
        self.sumXX  += xWt**2
        self.sumY   += yWt
        self.sumYY  += yWt**2
        self.sumXY  += xWt*yWt
        return self.count

    def SubtractWeighted(self, x, y, z):
        '''
        remove a weighted X,Y+/-Z trio from the statistics registers

        :param float x: value to remove
        :param float y: value to remove
        :param float z: variance (weight = ``1/z^2``) of y
        '''
        self._ClearResults_()
        weight = 1.0/(z**2)
        xWt = x*weight
        yWt = y*weight
        self.count  -= 1
        self.weight -= weight
        self.sumX   -= xWt
        self.sumXX  -= xWt**2
        self.sumY   -= yWt
        self.sumYY  -= yWt**2
        self.sumXY  -= xWt*yWt
        return self.count

    def Mean(self):
        '''
		arithmetic mean of X & Y

		.. math::

		  (1 / N) \\sum_i^N x_i

		:return: mean X and Y values
		:rtype: float
		'''
        if self.mean == None:
            self.mean = (self.sumX / self.weight, self.sumY / self.weight)
        return self.mean

    def __sdeverr(self, summation, sqr, weight):
        '''
		internal routine standard deviation and
		standard error of from given data
		'''
        temp = sqr - (summation**2)/weight
        if temp > 0:
            dev = math.sqrt(temp / weight)        # standard deviation
            err = math.sqrt(temp / (weight-1))    # standard error
        else:
            dev = 0
            err = 0
        return (dev, err)

    def StdDev(self):
        '''
		standard deviation on X & Y

		:return: standard deviation of mean X and Y values
		:rtype: (float, float)
		'''
        if self.sDev == None:
            xDev = self.__sdeverr(self.sumX, self.sumXX, self.weight)[0]
            yDev = self.__sdeverr(self.sumY, self.sumYY, self.weight)[0]
            self.sDev = (xDev, yDev)
        return self.sDev

    def StdErr(self):
        '''
		standard error on X & Y

		:return: standard error of mean X and Y values
		:rtype: (float, float)
		'''
        if self.sErr == None:
            xErr = self.__sdeverr(self.sumX, self.sumXX, self.weight)[1]
            yErr = self.__sdeverr(self.sumY, self.sumYY, self.weight)[1]
            self.sErr = (xErr, yErr)
        return self.sErr

    def LinearEval(self, x):
        '''
        Evaluate a linear fit at the given value: :math:`y = a + b x`

        :param x: independent value, `x`
        :type x: float
        :return: y
        :rtype: float
        '''
        self.LinearRegression()
        return self.intercept + x * self.slope

    def determinant(self):
        '''Compute and return the determinant of the square matrices.

        ::

          |  sum_w   sum_x      |          |  sum_w   sum_y      |
          |  sum_x   sum_(x^2)  |          |  sum_y   sum_(y^2)  |

        :return: determinants of x and y summation matrices
        :rtype: (float, float)
        '''
        if self.determ == None:
            x = self.weight*self.sumXX - self.sumX**2
            y = self.weight*self.sumYY - self.sumY**2
            self.determ = (x, y)
        return self.determ

    def LinearRegression(self):
        '''
        For (*x,y*) data pairs added to the registers,
        fit and find (*a,b*) that satisfy:

        .. math::

          y = a + b x

        :return: (a, b) for fit of y=a+b*x
        :rtype: (float, float)
        '''
        if self.slope == None or self.intercept == None:
            determ         = self.determinant()[0]
            self.slope     = (self.weight*self.sumXY - self.sumX*self.sumY) / determ
            self.intercept = (self.sumXX*self.sumY  - self.sumX*self.sumXY) / determ
        return (self.intercept, self.slope)

    def LinearRegressionVariance(self):
        '''
        est. errors of slope & intercept

        :return: (var_a, var_b) -- is this correct?
        :rtype: (float, float)
		'''
        if self.lrVariance == None:
            determ   = self.determinant()[0]
            slope    = math.sqrt (self.weight / determ)
            constant = math.sqrt (self.sumXX / determ)
            self.lrVariance = (constant, slope)
        return self.lrVariance

    def LinearRegressionCorrelation(self):
        '''
        the regression coefficient

        :return: (corr_a, corr_b) -- is this correct?
        :rtype: (float, float)

        :see: http://stattrek.com/AP-Statistics-1/Correlation.aspx?Tutorial=Stat
           Look at "Product-moment correlation coefficient"
		'''
        if self.r == None:
            VarX, VarY = self.determinant()
            self.r = (self.weight*self.sumXX - self.sumX*self.sumY) / math.sqrt(VarX*VarY)
        return self.r

    def CorrelationCoefficient(self):
        '''
        relation of errors in slope and intercept

        :return: correlation coefficient
        :rtype: float
		'''
        if self.correlation == None:
            self.correlation = -self.sumX / math.sqrt (self.weight * self.sumXX)
        return self.correlation

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def __selftest():
    """
    internal test StatsReg functions

    NOTES:

    https://en.ppt-online.org/186857
    slides 8-24

    https://data36.com/linear-regression-in-python-numpy-polyfit/

    https://en.wikipedia.org/wiki/Weighted_least_squares

    http://www.real-statistics.com/multiple-regression/weighted-linear-regression
    http://www.real-statistics.com/regression/least-squares-method/
    http://www.real-statistics.com/regression/regression-analysis/
    http://www.real-statistics.com/regression/deming-regression/deming-regression-basic-concepts/
    """
    import numpy as np

    print(f"{__selftest.__doc__.strip().splitlines()[0]}")
    print("---------------------------------------")

    print("create a set of stats registers")
    reg = StatsRegClass()
    reg.Show()
    print("---------------------------------------")

    print("add data to the stats registers")
    reg.Add(1, 1)
    reg.Add(-2, 2.01)
    reg.Add(1, 2)
    reg.Show()
    (xBar,        yBar)     = reg.Mean()
    (xBarDev,     yBarDev)  = reg.StdDev()
    print("\t%s: %g +/- %g" % ('<x>', xBar, xBarDev))
    print("\t%s: %g +/- %g" % ('<y>', yBar, yBarDev))
    print("---------------------------------------")

    print("subtract data from the stats registers")
    reg.Subtract(1, 1)
    reg.Show()
    (xBar,        yBar)     = reg.Mean()
    (xBarDev,     yBarDev)  = reg.StdDev()
    print("\t%s: %g +/- %g" % ('<x>', xBar, xBarDev))
    print("\t%s: %g +/- %g" % ('<y>', yBar, yBarDev))

    print("---------------------------------------")
    print("clear the stats registers")
    reg.Clear()
    reg.Show()
    print("---------------------------------------")

    print("linear regression test:")
    reg.Add(518, 1.101)
    reg.Add(519, 0.869)
    reg.Add(520, 0.674)
    reg.Add(521, 0.376)
    reg.Add(522, 0.143)
    reg.Show()
    (xBar,        yBar)     = reg.Mean()
    (xBarDev,     yBarDev)  = reg.StdDev()
    (constant,    slope)    = reg.LinearRegression()
    (constantVar, slopeVar) = reg.LinearRegressionVariance()
    print("\t%s: %g +/- %g" % ('constant', constant, constantVar))
    print("\t%s: %g +/- %g" % ('slope',    slope,    slopeVar))
    print("\tLinearRegressionCorrelation = %g" % reg.LinearRegressionCorrelation())
    print("\tCorrelationCoefficient = %g" % reg.CorrelationCoefficient())

    print("linear regression test (slope 1, intercept -2):")
    reg.Clear()
    for i in range(5):
        reg.Add(i, i-2 + 0.01*np.random.rand())
    reg.Show()
    (xBar,        yBar)     = reg.Mean()
    (xBarDev,     yBarDev)  = reg.StdDev()
    (constant,    slope)    = reg.LinearRegression()
    (constantVar, slopeVar) = reg.LinearRegressionVariance()
    print("\t%s: %g +/- %g" % ('constant', constant, constantVar))
    print("\t%s: %g +/- %g" % ('slope',    slope,    slopeVar))
    print("\tLinearRegressionCorrelation = %g" % reg.LinearRegressionCorrelation())
    print("\tCorrelationCoefficient = %g" % reg.CorrelationCoefficient())

    print("weighted linear regression test (slope 1, intercept -2):")
    reg.AddWeighted(1, 1, 1e10)
    reg.AddWeighted(-1, 1, 1e10)
    reg.AddWeighted(1, -1, 1e10)
    reg.AddWeighted(-1, -1, 1e10)
    reg.Show()
    (xBar,        yBar)     = reg.Mean()
    (xBarDev,     yBarDev)  = reg.StdDev()
    (constant,    slope)    = reg.LinearRegression()
    (constantVar, slopeVar) = reg.LinearRegressionVariance()
    print("\t%s: %g +/- %g" % ('constant', constant, constantVar))
    print("\t%s: %g +/- %g" % ('slope',    slope,    slopeVar))
    print("\tLinearRegressionCorrelation = %g" % reg.LinearRegressionCorrelation())
    print("\tCorrelationCoefficient = %g" % reg.CorrelationCoefficient())


if __name__ == '__main__':
    print(
        f"{os.path.split(sys.argv[0])[-1]}:"
        f" v{version}, "
        f" {__doc__.strip().splitlines()[0]}"
        )
    __selftest()
