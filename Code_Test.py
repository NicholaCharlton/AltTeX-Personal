# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 11:39:59 2023

@author: Nichola Charlton
"""


def find_character(eqn):
    for char in eqn:
        if char == "\\":
            print(char)


random = "g =\sin{1}\sin{\pi}\sin{2}"

find_character(random)





