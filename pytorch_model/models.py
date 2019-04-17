from __future__ import absolute_import
from __future__ import print_function

import logging
import os

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.nn.init as weight_init

logger = logging.getLogger(__name__)


class SkipAttention(nn.Module):
    def __init__(self, vocab_size, emb_size, hidden_size, n_layers=1):
        super(SkipAttention, self).__init__()
        self.emb_size = emb_size
        self.hidden_size = hidden_size
        self.n_layers = n_layers

        self.embedding = nn.Embedding(vocab_size, emb_size, padding_idx=0)
        self.lstm = nn.LSTM(emb_size, hidden_size, bidirectional=True, batch_first=True)
        for w in self.lstm.parameters():  # initialize the gate weights with orthogonal
            if w.dim() > 1:
                weight_init.orthogonal_(w)

    def forward(self, x_input, input_lengths=None):
        embedded = self.embedding(
            x_input)  # input: [batch_sz x seq_len]  embedded: [batch_sz x seq_len x emb_sz]
        embedded = F.dropout(embedded, 0.25, self.training)

        rnn_output, (final_hidden_state, final_cell_state) = self.lstm(
            embedded)  # out:[b x seq x hid_sz*2](biRNN)

        hidden = torch.cat([x for x in final_hidden_state], 1)
        attn_weights = torch.bmm(rnn_output, hidden.unsqueeze(2)).squeeze(2)
        soft_attn_weights = F.softmax(attn_weights, 1)
        new_hidden_state = torch.bmm(rnn_output.transpose(1, 2),
                                     soft_attn_weights.unsqueeze(2)).squeeze(2)
        encoding = F.tanh(new_hidden_state)
        return encoding


class DilatedCNN(nn.Module):
    def __init__(self, vocab_size, emb_size, hidden_size, n_layers=1):
        super(DilatedCNN, self).__init__()
        self.emb_size = emb_size
        self.hidden_size = hidden_size
        self.n_layers = n_layers

        self.embedding = nn.Embedding(vocab_size, emb_size, padding_idx=0)
        self.convs1 = nn.ModuleList(
            [nn.Conv2d(1, 80, (K, 100), dilation=1) for K in [1, 2, 3, 4, 5]])
        self.dropout = nn.Dropout(0.25)

    def forward(self, x_input, input_lengths=None):
        embedded = self.embedding(
            x_input)  # input: [batch_sz x seq_len]  embedded: [batch_sz x seq_len x emb_sz]
        embedded = F.dropout(embedded, 0.25, self.training)

        x_input = embedded.unsqueeze(1)
        x_input = [F.relu(conv(x_input)).squeeze(3) for conv in self.convs1]
        # print([i.shape for i in input])
        x_input = [F.max_pool1d(i, i.size(2)).squeeze(2) for i in x_input]
        x_input = torch.cat(x_input, 1)
        x_input = self.dropout(x_input)
        encoding = F.tanh(x_input)

        return encoding


class SeqEncoder(nn.Module):
    def __init__(self, vocab_size, emb_size, hidden_size, n_layers=1):
        super(SeqEncoder, self).__init__()
        self.emb_size = emb_size
        self.hidden_size = hidden_size
        self.n_layers = n_layers

        self.embedding = nn.Embedding(vocab_size, emb_size, padding_idx=0)
        self.lstm = nn.LSTM(emb_size, hidden_size, batch_first=True, bidirectional=True)
        for w in self.lstm.parameters():  # initialize the gate weights with orthogonal
            if w.dim() > 1:
                weight_init.orthogonal_(w)

    def forward(self, x_input: torch.Tensor, input_lengths=None):
        batch_size, seq_len = x_input.size()
        embedded = self.embedding(
            x_input)  # input: [batch_sz x seq_len]  embedded: [batch_sz x seq_len x emb_sz]
        embedded = F.dropout(embedded, 0.25, self.training)
        rnn_output, hidden = self.lstm(embedded)  # out:[b x seq x hid_sz*2](biRNN)
        rnn_output = F.dropout(rnn_output, 0.25, self.training)
        output_pool = F.max_pool1d(rnn_output.transpose(1, 2), seq_len).squeeze(
            2)  # [batch_size x hid_size*2]
        encoding = F.tanh(output_pool)

        return encoding


class JointEmbedding(nn.Module):
    def __init__(self, config):
        super(JointEmbedding, self).__init__()
        self.conf = config
        self.margin = config['margin']

        self.name_encoder = SeqEncoder(config['n_words'], config['emb_size'], config['lstm_dims'])
        self.api_encoder = SeqEncoder(config['n_words'], config['emb_size'], config['lstm_dims'])
        self.tok_encoder = SeqEncoder(config['n_words'], config['emb_size'], config['lstm_dims'])
        self.desc_encoder = SeqEncoder(config['n_words'], config['emb_size'], config['lstm_dims'])
        self.fuse = nn.Linear(6 * config['lstm_dims'], config['n_hidden'])

        # create a model path to store model info
        if not os.path.exists(config['workdir'] + 'models/'):
            os.makedirs(config['workdir'] + 'models/')

    def code_encoding(self, name, api, tokens):
        name_repr = self.name_encoder(name)
        api_repr = self.api_encoder(api)
        tok_repr = self.tok_encoder(tokens)
        code_repr = self.fuse(torch.cat((name_repr, api_repr, tok_repr), 1))
        code_repr = F.tanh(code_repr)
        return code_repr

    def desc_encoding(self, desc):
        desc_repr = self.desc_encoder(desc)
        return desc_repr

    def forward(self, name, apiseq, tokens, desc_good,
                desc_bad):  # self.data_params['methname_len']
        code_repr = self.code_encoding(name, apiseq, tokens)
        desc_good_repr = self.desc_encoding(desc_good)
        desc_bad_repr = self.desc_encoding(desc_bad)

        good_sim = F.cosine_similarity(code_repr, desc_good_repr)
        bad_sim = F.cosine_similarity(code_repr, desc_bad_repr)  # [batch_sz x 1]

        loss = (self.margin - good_sim + bad_sim).clamp(min=1e-6).mean()
        return loss
