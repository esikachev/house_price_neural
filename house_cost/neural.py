#!/usr/bin/env python
# -- coding: utf-8 --

__author__ = 'michael'

# Back-Propagation Neural Networks
#
# Written in Python.  See http://www.python.org/
# Placed in the public domain.
# Neil Schemenauer <nas@arctrix.com>

import math
import random
import string
random.seed(0)


district_map = {'Центр': 0.1, 'Спальный': 0.2, 'Окраина': 0.3}
square_map = {'< 50 м2':0.16, '50-100 м2':0.32, '100-150 м2':0.48, '150-200 м2':0.64, '200-250 м2':0.80, '> 250 м2':0.96}
room_map = {'1':0.1, '2':0.2, '3':0.3, '4':0.4, '5':0.5}
infra_map = {True:1, False:0}
year_map = {'70е':0.2, '80е':0.4, '90е':0.6, '00е':0.8, '10е':1}
remont_map = {True:1, False: 0}

# calculate a random number where:  a <= rand < b
def rand(a, b):
    return (b-a)*random.random() + a


# Make a matrix (we could use NumPy to speed this up)
def makeMatrix(iterate, jiterate, fill=0.0):
    m = []
    for i in range(iterate):
        m.append([fill]*jiterate)
    return m


# our sigmoid function, tanh is a little nicer than the standard 1/(1+e^-x)
def sigmoid(x):
    return math.tanh(x)


# derivative of our sigmoid function, in terms of the output (i.e. y)
def dsigmoid(y):
    return 1.0 - y**2


class NN:
    def __init__(self, ni, nh, no):
        # number of input, hidden, and output nodes
        self.ni = ni + 1  # +1 for bias node
        self.nh = nh
        self.no = no

        # activations for nodes
        self.ai = [1.0]*self.ni
        self.ah = [1.0]*self.nh
        self.ao = [1.0]*self.no

        # create weights
        self.wi = makeMatrix(self.ni, self.nh)
        self.wo = makeMatrix(self.nh, self.no)
        # set them to random vaules
        for i in range(self.ni):
            for j in range(self.nh):
                self.wi[i][j] = rand(-0.2, 0.2)
        for j in range(self.nh):
            for k in range(self.no):
                self.wo[j][k] = rand(-2.0, 2.0)

        # last change in weights for momentum
        self.ci = makeMatrix(self.ni, self.nh)
        self.co = makeMatrix(self.nh, self.no)

    def update(self, inputs):
        if len(inputs) != self.ni-1:
            raise ValueError('wrong number of inputs')

        # input activations
        for i in range(self.ni-1):
            # self.ai[i] = sigmoid(inputs[i])
            self.ai[i] = inputs[i]

        # hidden activations
        for j in range(self.nh):
            sum = 0.0
            for i in range(self.ni):
                sum += self.ai[i] * self.wi[i][j]
            self.ah[j] = sigmoid(sum)

        # output activations
        for k in range(self.no):
            sum = 0.0
            for j in range(self.nh):
                sum += self.ah[j] * self.wo[j][k]
            self.ao[k] = sigmoid(sum)

        return self.ao[:]

    def backPropagate(self, targets, N, M):
        if len(targets) != self.no:
            raise ValueError('wrong number of target values')

        # calculate error terms for output
        output_deltas = [0.0] * self.no
        for k in range(self.no):
            error = targets[k]-self.ao[k]
            output_deltas[k] = dsigmoid(self.ao[k]) * error

        # calculate error terms for hidden
        hidden_deltas = [0.0] * self.nh
        for j in range(self.nh):
            error = 0.0
            for k in range(self.no):
                error += output_deltas[k]*self.wo[j][k]
            hidden_deltas[j] = dsigmoid(self.ah[j]) * error

        # update output weights
        for j in range(self.nh):
            for k in range(self.no):
                change = output_deltas[k]*self.ah[j]
                self.wo[j][k] = self.wo[j][k] + N*change + M*self.co[j][k]
                self.co[j][k] = change
                # print N*change, M*self.co[j][k]

        # update input weights
        for i in range(self.ni):
            for j in range(self.nh):
                change = hidden_deltas[j]*self.ai[i]
                self.wi[i][j] = self.wi[i][j] + N*change + M*self.ci[i][j]
                self.ci[i][j] = change

        # calculate error
        error = 0.0
        for k in range(len(targets)):
            error += 0.5*(targets[k]-self.ao[k])**2
        return error

    def test(self, patterns):
        for p in patterns:
            #print(p[0], '->', self.update(p[0]))
            return self.update(p[0])[0]

    def weights(self):
        print('Input weights:')
        for i in range(self.ni):
            print(self.wi[i])
        print()
        print('Output weights:')
        for j in range(self.nh):
            print(self.wo[j])

    def train(self, patterns, iterations=50000, N=0.5, M=0.1):
        # N: learning rate
        # M: momentum factor
        for i in range(iterations):
            try:
                error = 0.0
                for p in patterns:
                    inputs = p[0]
                    targets = p[1]
                    self.update(inputs)
                    error += self.backPropagate(targets, N, M)
                if i % 100 == 0:
                    print('error %-.5f' % error)
            except KeyboardInterrupt:
                print i
                raise SystemExit

    def save(self, fname):
        # открываем фал, в который будем записывать НС
        f = open(fname, "w")
        # записываем количество нейронов во входном, скрытом и выходном слоях
        f.write(str(self.ni)+";")
        f.write(str(self.nh)+";")
        f.write(str(self.no)+";")
        # записываем весовые коэффициенты между нейронами входного и скрытого слоев
        for i in xrange(self.ni):
            for j in xrange(self.nh):
                f.write(str(self.wi[i][j])+";")
        # записываем весовые коэффициенты между нейронами скрытого и выходного слоев
        for i in xrange(self.nh):
            for j in xrange(self.no):
                f.write(str(self.wo[i][j])+";")
        # закрываем файл
        f.close()

    def load(self, fname):
        # открываем файл для чтения
        f = open(fname, "r")
        # считываем содержимое файла в переменную line, и закрываем файл
        line = f.read()
        f.close()
        # представляем данные в виде массива строк
        arr = string.split(line, ";")
        # получаем количество нейронов во входном, скрытом и выходном слоях
        self.ni, self.nh, self.no = int(arr[0]), int(arr[1]), int(arr[2])
        # создаем матрицы весовых коэффициентов соответствующих размеров
        self.wi = makeMatrix(self.ni, self.nh)
        self.wo = makeMatrix(self.nh, self.no)
        # устанавливаем счетчик считанных элементов
        n = 2
        # считываем весовые коэффициенты между нейронами входного и скрытого слоев
        for i in xrange(self.ni):
            for j in xrange(self.nh):
                n += 1
                self.wi[i][j] = float(arr[n])
        # считываем весовые коэффициенты между нейронами скрытого и выходного слоев
        for i in xrange(self.nh):
            for j in xrange(self.no):
                n += 1
                self.wo[i][j] = float(arr[n])


def demo():
    """
    +----------------+----------------------------------------------------------------+
    |Район           |Центр, Cпальный, Окраинa                                        |
    +----------------+----------------------------------------------------------------+
    |Площадь дома    |< 50 м2, 50-100 м2, 100-150 м2, 150-200 м2, 200-250 м2, > 250 м2|
    +----------------+----------------------------------------------------------------+
    |Кол-во комнат   |1, 2, 3, 4, 5                                                   |
    +----------------+----------------------------------------------------------------+
    |Инфраструктура  |Развитая, Не очень(чекбокс)                                    |
    +----------------+----------------------------------------------------------------+
    |Тип(Год)        |70е, 80е, 90е, 00е, 10е                                         |
    +----------------+----------------------------------------------------------------+
    |Ремонт          |Да, Нет(чекбокс)                                                |
    +----------------+----------------------------------------------------------------+
    :return:
    """

    #pat = dataset_factor.dataset_fabric()
    new_pat=[[[0.1, 0.32, 0.4, 1, 0.6, 0]]] # 0.09
    # create a network with two input, two hidden, and one output nodes
    #n = NN(6, 2, 1)
    # train it with some patterns
    #n.train(pat)
    n = NN(6, 2, 1)
    n.load('house_cost/network.nn')
    #n.save('house_cost/network.nn')
    # test it
    n.test(new_pat)


#if __name__ == '__main__':
    #demo()
