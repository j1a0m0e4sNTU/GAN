import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from util import *
import cv2 as cv
import os
import sys

def get_string(*args):
    string = ''
    for s in args:
        string = string + ' ' + str(s)
    return string


class Manaeger():
    def __init__(self, model_G, model_D, args):
        
        if  args.load:
            load_name = os.path.join('../weights/', args.load)
            model_G.load_state_dict(torch.load(load_name + '_G.pkl'))
            model_D.load_state_dict(torch.load(load_name + '_D.pkl'))
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_G = model_G.to(self.device)
        self.model_D = model_D.to(self.device)
        self.id = args.id
        self.lr = args.lr
        self.optimizer_G = optim.Adam(self.model_G.parameters(), lr= self.lr)
        self.optimizer_D = optim.Adam(self.model_D.parameters(), lr= self.lr)
        self.epoch_num = args.epoch_num
        self.batch_size = args.batch_size
        self.bce_loss = nn.BCELoss()
        
        self.save_name_G = os.path.join('../weights/', self.id + '_G.pkl') 
        self.save_name_D = os.path.join('../weights/', self.id + '_D.pkl') 
        self.log_file = open('logs/' + self.id + '.txt', 'w')
        self.check_batch_num = args.check_batch_num
        self.gen_dir = os.path.join('generations', args.gen_dir)
        os.mkdir(self.gen_dir)
    
    def load_data(self, train_loader, valid_loader):
        self.train_loader = train_loader
        self.valid_loader = valid_loader

    def record(self, message):
        self.log_file.write(message)
        print(message, end='')

    def get_info(self):
        info = get_string('\nModel:', self.model.name(), '\n')
        info = get_string(info, 'Learning rate:', self.lr, '\n')
        info = get_string(info, 'Epoch number:', self.epoch_num, '\n')
        info = get_string(info, 'Batch size:', self.batch_size, '\n')
        info = get_string(info, 'Weight name:', self.save_name, '\n')
        info = get_string(info, 'Log file:', self.log_file, '\n')
        info = get_string(info, '=======================\n\n')
        return info

    def train(self):
        info = self.get_info()
        self.record(info)
        
        for epoch in range(self.epoch_num):
            self.model.train()
            
            for batch_id, imgs in enumerate(self.train_loader):
                imgs = imgs.to(self.device)
    

    def generate(self):
        pass