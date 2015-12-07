#!/usr/bin/env python
# -- coding: utf-8 --
from __future__ import division

def dataset_fabric():
    #
    dataset = []
    for a in [0.1, 0.2, 0.3]:
        for b in [0.16, 0.32, 0.48, 0.64, 0.80, 0.96]:
            for c in [0.1, 0.2, 0.3, 0.4, 0.5]:
                for d in [1, 0]:
                    for e in [0.2, 0.4, 0.6, 0.8, 1]:
                        for f in [1, 0]:
                            # summa - Общая стоимость дома. Измеряется в сотнях тысяч, для
                            # восприятия сетью, разделим данное число на 100
                            summma = 0
                            if a == 0.1:
                                summma += 4
                            elif a == 0.2:
                                summma += 2
                            else:
                                summma += 1
                            if b == 0.16:
                                summma += 0.5
                            elif b == 0.32:
                                summma += 1
                            elif b == 0.48:
                                summma += 1.5
                            elif b == 0.64:
                                summma += 2
                            elif b == 0.80:
                                summma += 2.5
                            else:
                                summma += 3
                            if c == 0.1:
                                summma += 1
                            elif c == 0.2:
                                summma += 1.5
                            elif c == 0.3:
                                summma += 1.7
                            elif c == 0.4:
                                summma += 2
                            else:
                                summma += 2.2
                            if d == 1:
                                summma += 2.5
                            else:
                                summma += 1
                            if e == 0.2:
                                summma += 0.5
                            elif e == 0.4:
                                summma += 0.8
                            elif e == 0.6:
                                summma += 1
                            elif e == 0.8:
                                summma += 1.5
                            else:
                                summma += 2
                            if f == 1:
                                summma += 1.5
                            else:
                                summma += 0.5
                            summma /= 100
                            summma = round(summma, 5)
                            summary = []
                            summary.append(summma)
                            mnoz = []
                            mnoz.append(a)
                            mnoz.append(b)
                            mnoz.append(c)
                            mnoz.append(d)
                            mnoz.append(e)
                            mnoz.append(f)
                            obsch = []
                            obsch.append(mnoz)
                            obsch.append(summary)

                            dataset.append(obsch)
                            #print '['+'['+str(a)+', '+str(b)+', '+str(c)+', '+str(d)+', '+str(e)+', '+str(f)+'], ['+str(summma)+']'+'],'

    return dataset

