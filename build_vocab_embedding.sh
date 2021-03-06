#!/usr/bin/env bash
#
# build_vocab_embedding.sh
# Copyright (C) 2019 LeonTao
#
# Distributed under terms of the MIT license.
#



python misc/build_vocab_embedding.py \
    --data_path ./data/dmsc_v2_ratings_augment.txt \
    --data_dir ./data/ \
    --vocab_size 12000 \
    --wordvec_file ./embedding/word2vec/data/merge.web.2.cbow.negative.100.bin \
	--embedding_size 100 \

/

