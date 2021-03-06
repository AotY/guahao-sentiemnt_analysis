#!/usr/bin/env bash

python misc/preprocess.py \
    --data_dir /home/deep/Public/Research/guaho-spider/data_raw/ \
    --userdict ./data/userdict.txt \
    --label_cleaned_path ./data/label.cleaned.txt \
    --score_cleaned_path ./data/score.cleaned.txt \
    --vocab_freq_path ./data/vocab.freq.txt \
    --save_dir ./data \
    --min_len 3 \
    --max_len 300 \
    #--data_dir ./data/raw/ \
