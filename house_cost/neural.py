#!/usr/bin/env python
# -- coding: utf-8 --

# Back-Propagation Neural Networks
#
# Written in Python.  See http://www.python.org/
# Placed in the public domain.
# Neil Schemenauer <nas@arctrix.com>

import math
import random
import string
random.seed(0)


district_map = {'BMW': 0.1, 'Audi': 0.2, 'Mercedes': 0.3}
square_map = {'< 50000 км': 0.96, '50000-100000 км': 0.80,
              '100000-150000 км': 0.64, '150000-200000 км': 0.48,
              '200000-250000 км': 0.32, '> 250000 км': 0.16}
room_map = {'1.6 л': 0.1, '1.8 л': 0.2, '2 л': 0.3, '2.5 л': 0.4, '3 л': 0.5}
infra_map = {True: 1, False: 0}
year_map = {'80е - 90е': 0.2, '90е - 2000г': 0.4, '2000г - 2005г': 0.6, '2005г - 2010г': 0.8, '2010е': 1}
remont_map = {True: 1, False: 0}


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
    """
    Функции:
    update - обновить веса сети
    backPropagate - алгоритм обратного распространения ошибки
    simulate - произвести вычисления на уже обученной нейронной сети
    weight - рассчет весов внутри сети
    train - тренировка сети
    save - сохранить сеть в файл
    load - загрузить сеть в файл
    """
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

    def simulate(self, patterns):
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
