import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import time

rnstate = np.random.RandomState(1)
x = 10*rnstate.rand(50)
y = 2*x+rnstate.randn(50)

model = LinearRegression(fit_intercept=True)
model.fit(x[:, np.newaxis], y)
xfit = np.linspace(0,10,1000)
yfit = model.predict(xfit[:,np.newaxis])

plt.scatter(x,y)
plt.plot(xfit, yfit)
plt.ylabel("y-axis")
plt.xlabel("x-axis")
plt.title("graphs get titles")
plt.draw()
plt.pause(10)
plt.close()
print("close")