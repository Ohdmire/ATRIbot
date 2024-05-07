import numpy as np
from scipy.optimize import leastsq


class Tools:

    def leastsquares(self, list1, list2):

        # 样本数据(Xi,Yi)，需要转换成数组(列表)形式
        Xi = np.array(list1)
        Yi = np.array(list2)

        # 需要拟合的函数func :指定函数的形状 k= 0.42116973935 b= -8.28830260655

        def func(p, x):
            k, b = p
            return k * x + b

        # 偏差函数：x,y都是列表:这里的x,y更上面的Xi,Yi中是一一对应的

        def error(p, x, y):
            return func(p, x) - y

        # k,b的初始值，可以任意设定,经过几次试验，发现p0的值会影响cost的值：Para[1]
        p0 = [1, 20]

        # 把error函数中除了p0以外的参数打包到args中(使用要求)
        Para = leastsq(error, p0, args=(Xi, Yi))

        # 读取结果
        k, b = Para[0]
        print("k=", k, "b=", b)
        return k, b
