from boxplot import *

a = [1,2,3,4,5,6,7,8,9, 69734, -4344]
b = [1,2,3,4,5,6,7,8, -21, 775]
c = [1,5, 69]

x = [1,2,3,4,5,6,7,8,9]
y = [1,2,3,4,5,6,7,8]
z = [1,5]

def test_mediana():
    assert boxplot.mediana(x) == 5
    assert boxplot.mediana(y) == 4.5
    assert boxplot.mediana(z) == 3

def test_quartis():
    assert boxplot.quartis(x, raw=True) == "min: -5.00, q1: 2.50, q2: 5.00, q3: 7.50, max: 15.00"
    assert boxplot.quartis(y, raw=True) == "min: -3.50, q1: 2.50, q2: 4.50, q3: 6.50, max: 12.50"
    assert boxplot.quartis(z, raw=True) == "min: -5.00, q1: 1.00, q2: 3.00, q3: 5.00, max: 11.00"

def test_atipicos():
    assert boxplot.atipicos(a) == [69734, -4344]
    assert boxplot.atipicos(b) == [-21, 775]
    assert boxplot.atipicos(c) == []

    assert boxplot.atipicos(x) == []
    assert boxplot.atipicos(y) == []
    assert boxplot.atipicos(z) == []
