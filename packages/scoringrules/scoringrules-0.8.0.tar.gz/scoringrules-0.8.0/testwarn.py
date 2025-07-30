import numpy as np

import scoringrules as sr 

obs = np.random.randn(3,5)
fct = np.random.randn(3, 4, 5)

res = sr.energy_score(obs, fct)