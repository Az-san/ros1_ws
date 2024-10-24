#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import numpy as np
import random


#==================================================

## @fn randomChoices
## @brief random.choicesを自分で実装したやつ
## @param population 重み付きの抽選を行われるリスト
## @param weight 重み
## @return

#==================================================
def randomChoices(
    population,
    weight
):
    np_w = np.array(weight)
    opp = 0
    # 最小値がゼロ以下なら、下駄oppを履かせる(最小値が１となる)
    if np.min(np_w) <= 0:
        opp = abs(np.min(np_w)) + 1
        np_w += opp

    upp = np.sum(np_w)
    rnd = random.randint(0, upp-1)
    inc = 0

    for i in range(len(np_w)):
        inc += np_w[i]
        if rnd < inc:
            
            return population[i]

if __name__ == '__main__':
    population = [0,1,2,3]
    weight = [0,0,0,0]
    vote = [0,0,0,0]

    for i in range(1000):
        a = randomChoices(population, weight)
        vote[a] += 1

    print(vote)

