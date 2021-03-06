#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2019 LeonTao
#
# Distributed under terms of the MIT license.

"""
Data Augmentation using Thesaurus
"""

import sys
import argparse
from tqdm import tqdm
import numpy as np

parser = argparse.ArgumentParser()

parser.add_argument('--data_path', type=str, help='')
parser.add_argument('--syno_path', type=str, help='', default='./data/syno.txt')
parser.add_argument('--cilin_path', type=str, help='', default='./data/cilin_ex.txt')
parser.add_argument('--save_path', type=str, help='')
#  parser.add_argument('--augment_num', type=int, help='', default=2)
parser.add_argument('--augment_nums', nargs='+', type=int, help='')
parser.add_argument('--augment_labels', nargs='+', type=int, help='')

args = parser.parse_args()


print('Loading syno...')
line_set = set()
syno_dict = {}
with open(args.syno_path, 'r') as f:
    #  for line in tqdm(f):
    for line in f:
        line = line.rstrip()
        if line in line_set:
            continue
        line_set.add(line)
        try:
            w1, w2 = line.split()
        except ValueError as e:
            print(line)

        if len(w1) == 1 or len(w2) == 1:
            continue

        if syno_dict.get(w1) is None:
            syno_dict[w1] = list()

        if syno_dict.get(w2) is None:
            syno_dict[w2] = list()

        if w2 not in syno_dict[w1]:
            syno_dict[w1].append(w2)

        if w1 not in syno_dict[w2]:
            syno_dict[w2].append(w1)

print('Loading cilin...')
with open(args.cilin_path, 'r') as f:
    for line in f:
        line = line.rstrip()
        words = line.split()
        if len(words) == 2:
            continue
        words = words[1:]
        for w1 in words:
            if syno_dict.get(w1) is None:
                syno_dict[w1] = list()
            for w2 in words:
                if w1 != w2 and w2 not in syno_dict[w1]:
                    syno_dict[w1].append(w2)

print('Loading label data...', args.augment_labels)
label_datas = {}
label_augment_num_dict = {}
for label, augment_num in zip(args.augment_labels, args.augment_nums):
    label_datas[label] = list()
    label_augment_num_dict[label] = augment_num

save_file = open(args.save_path, 'w')
with open(args.data_path, 'r') as f:
    for line in tqdm(f):
        save_file.write(line)
        line = line.rstrip()
        label, text = line.split('\t')

        label = int(label)
        if label in args.augment_labels:
            label_datas[label].append(text)

for label, label_data in label_datas.items():
    augment_num = label_augment_num_dict[label]
    for text in label_data:
        words = text.split()
        syno_words = list()
        for idx, word in enumerate(words):
            if word in syno_dict:
                syno_words.append((idx, word))
        if len(syno_words) == 0:
            continue

        for _ in range(augment_num):
            new_words = words.copy()
            #  augment_count = int(np.random.geometric(p=0.5, size=1))
            #  if augment_count > len(syno_words):
            #  augment_count = len(syno_words)
            augment_count = np.random.randint(low=1, high=len(syno_words) + 1)

            for idx, word in syno_words[:augment_count]:
                chose_idx = int(np.random.geometric(p=0.5, size=1))
                if chose_idx >= len(syno_dict[word]):
                    chose_idx = len(syno_dict[word]) - 1
                new_words[idx] = syno_dict[word][chose_idx]
            save_file.write('%s\t%s\n' % (label, ' '.join(new_words)))

print('Augment success.')
