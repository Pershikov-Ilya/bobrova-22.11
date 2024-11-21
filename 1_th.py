from math import exp, factorial
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import poisson, chi2

demand_values = np.array([0, 1, 2, 3, 4])
demand_probs = np.array([0.3, 0.36, 0.22, 0.09, 0.03])

restock_days = np.array([2, 3, 4, 5])
restock_probs = np.array([0.1, 0.5, 0.3, 0.1])

mean_demand = 1.19
var_demand = 1.114
sr = (mean_demand + var_demand)/2

# (возвр. кол-во значений)случайное значение спроса (пуассон)
def poiss_gen(lbd):
    y = 0
    S = -np.log(np.random.rand())
    while S <= lbd:
        y += 1
        S -= np.log(np.random.rand())
    return y


work_days = 5
weeks = 5
total_days = work_days * weeks
details = 10
deficit = []
all_demand = []
day_new_order = 6
order = False
demand_all = []


# Каждый день генерируется спрос.
# Если деталей меньше 7 в конце недели, делается заказ.
# Если спрос превышает запасы, происходит дефицит.
for day in range(total_days):
    demand = poiss_gen(sr)
    demand_all.append(demand)

    # Если заказ не сделан, и деталей меньше 7, и это последний день недели, делается заказ.
    if not order and details < 7 and day % 5 == 0:
        order = True
        day_new_order = np.random.choice(restock_days, p=restock_probs)

    if details >= demand:
        # Если деталей хватает, то их количество уменьшается на размер спроса.
        all_demand.append(details-demand)
        details -= demand
    else:
        # Если деталей недостаточно, фиксируется дефицит, и детали обнуляются.
        all_demand.append(0)
        deficit.append(day)
        details = 0


    # Если заказ был сделан, отсчитывается время до его выполнения.
    # Как только время доставки истекает, заказанный объем добавляется на склад.
    if order:
        day_new_order -= 1
        if day_new_order == 0:
            order = False
            details += 10



# генерация 25 значений выборки из распределения Пуассона с параметром λ.
N = 25
lambda_param = sr

# Генерация выборки
vib = [poisson.rvs(mu=lambda_param) for _ in range(N)]

# подсчет частоты спроса по всем дням
prom = np.arange(min(demand_all), max(demand_all) + 1)
count_vib = [np.sum(np.array(demand_all) == i) for i in prom]

# Нормировка частоты
count_vib_normalized = np.array(count_vib) / N

# Теоретические значения
Y = (lambda_param ** prom) * np.exp(-lambda_param) / np.array([factorial(i) for i in prom])

# Проверяется гипотеза о соответствии наблюдаемого распределения
# теоретическому распределению Пуассона.
x2emp = np.sum(((count_vib - N * Y) ** 2) / (N * Y))
x2kr = chi2.ppf(0.95, len(prom) - 1)  # уровень значимости 0.05

if x2emp < x2kr:
    print("Гипотеза не отвергается")
else:
    print("Гипотеза отвергается")



plt.figure(figsize=(10, 6))
plt.plot(range(total_days), (all_demand), label="Накопленный спрос")
plt.scatter(deficit, [all_demand[s] for s in deficit], color="red", label="Дефицит")
plt.xlabel("Дни")
plt.ylabel("Накопленный спрос")
plt.legend()
plt.title("Потребность в деталях и дефицит запасов за время")
plt.show()
