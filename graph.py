import matplotlib.pyplot as plt
import pandas as pd

f = pd.read_csv("result.csv")
print(f)
f.plot("temps","valeur")
plt.show()