#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Transformer
"""
import torch
import torch.nn as nn
import torch.nn.functional as F

from modules.transformer.encoder import Encoder
from modules.utils import rnn_factory


class Transformer(nn.Module):
    ''' A sequence to sequence model with attention mechanism. '''

    def __init__(self, config, embedding):
        super().__init__()

        self.problem = config.problem

        self.embedding = embedding
        self.embedding_size = embedding.embedding_dim

        self.model_type = config.model_type
        self.n_classes = config.n_classes
        self.dense_size = config.dense_size

        #  self.transformer_size = config.transformer_size
        self.max_len = config.max_len

        self.encoder = Encoder(
            config,
            embedding
        )

        if self.model_type == 'transformer':
            in_feature_size = self.embedding_size * self.max_len
        elif self.model_type == 'transformer_mean':
            self.linear_dense = nn.Linear(
                self.embedding_size,
                self.dense_size
            )
            in_feature_size = self.dense_size

        elif self.model_type == 'transformer_rnn':
            self.bidirection_num = 2 if config.bidirectional else 1
            self.hidden_size = self.embedding_size // self.bidirection_num

            # rnn
            self.rnn = rnn_factory(
                rnn_type=config.rnn_type,
                input_size=self.embedding_size,
                hidden_size=self.hidden_size,
                num_layers=config.num_layers,
                bidirectional=config.bidirectional,
                dropout=config.dropout
            )

            in_feature_size = self.dense_size = self.hidden_size * self.bidirection_num
        elif self.model_type == 'transformer_weight':
            # W_s1
            self.linear_first = torch.nn.Linear(self.embedding_size, config.dense_size)
            self.linear_first.bias.data.fill_(0)

            # W_s2
            self.linear_second = torch.nn.Linear(config.dense_size, config.num_heads)
            self.linear_second.bias.data.fill_(0)
            in_feature_size = config.max_len * config.num_heads

        if self.problem == 'classification':
            self.linear_final = nn.Linear(in_feature_size, config.n_classes)
        else:
            self.linear_regression_dense = nn.Linear(in_feature_size, config.regression_dense_size)
            self.linear_regression_final = nn.Linear(config.regression_dense_size, 1)

        # nn.init.xavier_normal_(self.linear_final.weight)

    def forward(self,
                inputs,
                inputs_pos):
        """
        Args:
            inputs: [batch_size, max_len]
            inputs_pos: [batch_size, max_len]
        return: [batch_size, n_classes], [batch_size * num_heads, max_len, max_len] list
        """
        # [batch_size, max_len, embedding_size] list
        outputs, attns = self.encoder(inputs, inputs_pos, return_attns=True)
        # print('outputs shape: ', outputs.shape)
        # print('attns[0] shape: ', attns[0].shape)
        # print('attns[-1] shape: ', attns[-1].shape)


        # to [batch_size, n_classes]
        if self.model_type == 'transformer':
            # [batch_size, max_len * embedding_size]
            outputs = outputs.view(outputs.size(0), -1)
        elif self.model_type == 'transformer_mean':  # mean, average
            # [batch_size, embedding_size]
            outputs = outputs.mean(dim=1)
            outputs = self.linear_dense(outputs)
            outputs = F.relu(outputs)
            # [batch_size, n_classes]
        elif self.model_type == 'transformer_rnn':  # with or without position embedding
            outputs, _ = self.rnn(outputs.transpose(0, 1))
            outputs = outputs[-1]
        elif self.model_type == 'transformer_weight':
            # [batch_size, max_len, dense_size]
            x = F.tanh(self.linear_first(outputs))

            # [batch_size, max_len, num_heads]
            x = self.linear_second(outputs)

            # [batch_size, n_classes]
            outputs = x.view(x.size(0), -1)

        if self.problem == 'classification':
            outputs = self.linear_final(outputs)
        else:
            outputs = self.linear_regression_dense(outputs)
            outputs = self.linear_regression_final(outputs)

        # [batch_size, vocab_size]
        return outputs, attns
