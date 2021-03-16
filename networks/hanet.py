#!/usr/bin/env python
# coding: utf-8

import warnings
import torch
import torch.nn as nn
import torch.nn.functional as F
import positional_encodings as pe


class Conv1dPosEncRelu(nn.Module):
    """ Convolution 1D + Positional Encoding + ReLU module """

    def __init__(self, in_channels, out_channels, kernel_size=1, stride=1,
                            padding=0, bias=True, positional_encoding=True):
        super(Conv1dPosEncRelu, self).__init__()
        self.out_channels = out_channels
        self.pos_enc = positional_encoding
        self.conv = nn.Conv1d(in_channels, out_channels, kernel_size=kernel_size, 
                                        stride=stride, padding=padding, bias=bias)
        self.relu = nn.ReLU()

    def forward(self, inputs):
        Q = self.conv(inputs)
        if self.pos_enc:
            encoder = pe.PositionalEncodingPermute1D(self.out_channels)
            PE = encoder(torch.zeros(Q.size()))
            Q = Q + PE
        outputs = self.relu(Q)
        return outputs 

class Conv1dPosEncSigmoid(nn.Module):
    """ Convolution 1D + Positional Encoding + Sigmoid module """

    def __init__(self, in_channels, out_channels, kernel_size=1, stride=1,
                            padding=0, bias=True, positional_encoding=True):
        super(Conv1dPosEncSigmoid, self).__init__()
        self.out_channels = out_channels
        self.pos_enc = positional_encoding
        self.conv = nn.Conv1d(in_channels, out_channels, kernel_size=kernel_size, 
                                        stride=stride, padding=padding, bias=bias)
        self.sigmoid = nn.Sigmoid()

    def forward(self, inputs):
        Q = self.conv(inputs)
        if self.pos_enc:
            encoder = pe.PositionalEncodingPermute1D(self.out_channels)
            PE = encoder(torch.zeros(Q.size()))
            Q = Q + PE
        outputs = self.sigmoid(Q)
        return outputs  

class HANet(nn.Module):
    """ Height-driven Attention Networks (HaNet) class """

    def __init__(self, l_dims, h_dims, ww_pool="average", attention_height=16, 
                    reduction_ratio=32,n_convolutions=3, positional_encoding=True):
        """ Initialize an instance of HANet. 

            Parameters:
                l_dims ([int, int, int]): lower-level dimensions
                h_dims ([int, int, int]): higher-level dimensions
                ww_pool ({"average", "max"}): width-wise pooling type
                attention_height (int): height of the attention's map
                reduction_ratio (int): reduction ratio
                n_convolutions (int): number of convolutions to create the attention 
                map
                position_encoding (bool): determines if positional encoding is
                injected after each convolution.
        """
        assert len(l_dims) == 3, "all input dimensions CxHxW have to be provided"
        assert len(h_dims) == 3, "all output dimensions CxHxW have to be provided"
        assert ww_pool in ["average", "max"], "width-wise pooling can only be 'average' or 'max'"
        assert n_convolutions >= 1, "at least one convolution is needed"

        super(HANet, self).__init__()
        self.C_l, self.H_l, self.W_l = l_dims
        self.C_h, self.H_h, self.W_h = h_dims
        self.a_height = attention_height     
        self.r = reduction_ratio  
        self.n_convolutions = n_convolutions
        self.pos_enc = positional_encoding

        # G_pool
        if ww_pool == "average":
            self.ww_pooling = nn.AvgPool2d(kernel_size=(1, self.W_l), stride=(1,1))
        else:
            self.ww_pooling = nn.MaxPool2d(kernel_size=(1, self.W_l), stride=(1,1))
        # G_down
        self.down = nn.Upsample(size=(self.a_height, 1), mode="bilinear", align_corners=False)
        # G_conv1, G_conv2, ..., G_convN
        self.convs = self._generate_convolutions()
        # G_up
        self.up = nn.Upsample(size=(self.H_h, 1), mode="bilinear", align_corners=False)

    def _generate_convolutions(self):
        """ Generate the necessary convolutions to create the attention map """
        layers = []
        
        if (self.C_l // self.r) == 0 and self.n_convolutions > 1:
            warnings.warn("lower-level channels too small for the given reduction_ratio - n_convolutions set to 1")
            self.n_convolutions = 1

        in_channels = self.C_l
        for i in range(1, self.n_convolutions):
            out_channels = i * (self.C_l // self.r) # i * (C_l / r)
            layers.append(
                Conv1dPosEncRelu(in_channels, out_channels, positional_encoding=self.pos_enc)
            )
            in_channels = out_channels
        layers.append(
            Conv1dPosEncSigmoid(in_channels, self.C_h, positional_encoding=self.pos_enc)
        )

        return nn.Sequential(*layers)

    def forward(self, X_l): 
        """ Compute attention map 

            Parameters:
                X_l (torch.Tensor): low-level input
            
            Return:
                (torch.Tensor): height-driven attention map
        """
        # print("X_l = ", X_l.size()[1:])
        Z = self.ww_pooling(X_l)
        # print("Z = ", Z.size()[1:])
        Z_hat = self.down(Z)
        Z_hat = Z_hat.squeeze(-1)
        # print("Z_hat = ", Z_hat.size()[1:])
        Q = self.convs[0](Z_hat)
        # print(" Q_1 = ", Q.size()[1:])
        for i in range(1, self.n_convolutions):
            Q = self.convs[i](Q)
            # print(" Q_{} = ".format(i+1), Q.size()[1:])
        A_hat = Q.unsqueeze(-1)
        # print("A_hat = ", A_hat.size()[1:])
        A = self.up(A_hat)
        # print("A = ", A.size()[1:])
        return A
        