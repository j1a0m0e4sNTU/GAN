import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from util import *
import cv2 as cv
import os
import sys

class Manaeger():
    def __init__(self, model_G, model_D, args):
        
        if  args.load:
            load_name = os.path.join('../weights/', args.load)
            model_G.load_state_dict(torch.load(load_name + '_G.pkl'))
            model_D.load_state_dict(torch.load(load_name + '_D.pkl'))
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_G = model_G.to(self.device)
        self.latent_dim = model_G.get_latent_dim()
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
        self.gen_dir = os.path.join('generations', args.id)
        if not os.path.isdir(self.gen_dir):
            os.mkdir(self.gen_dir)
    
    def load_data(self, data_loader):
        self.data_loader = data_loader
        
    def record(self, message):
        self.log_file.write(message)
        print(message, end='')

    def get_info(self):
        info = get_string('\nID:', self.id, '\n')
        info = get_string(info, 'Generator:', self.model_G.name(), '\n')
        info = get_string(info, 'Discriminator:', self.model_D.name(), '\n')
        info = get_string(info, 'Learning rate:', self.lr, '\n')
        info = get_string(info, 'Epoch number:', self.epoch_num, '\n')
        info = get_string(info, 'Batch size:', self.batch_size, '\n')
        info = get_string(info, '=======================\n\n')
        return info

    def train(self):
        info = self.get_info()
        self.record(info)

        for epoch in range(self.epoch_num):
            self.model_G.train()
            self.model_D.train()
            img_gen = None
            
            for batch_id, imgs in enumerate(self.data_loader):

                vector = self.get_input_vector()
                label_valid = torch.ones(self.batch_size, 1).to(self.device)
                label_fake  = torch.zeros(self.batch_size, 1).to(self.device)
            
                # Train Disciminator
                self.model_D.zero_grad()
                self.optimizer_D.zero_grad()
                img_valid = imgs.to(self.device)
                img_gen = self.model_G(vector)

                loss_valid = self.bce_loss(self.model_D(img_valid), label_valid)
                loss_fake  = self.bce_loss(self.model_D(img_gen.detach()), label_fake)
                loss_D = (loss_valid + loss_fake) 
                loss_D.backward()
                self.optimizer_D.step()
                
                # Train Generator
                self.model_G.zero_grad()
                self.optimizer_G.zero_grad()
                loss_G = self.bce_loss(self.model_D(img_gen), label_valid)
                loss_G.backward()
                self.optimizer_G.step()

                if (batch_id + 1) % self.check_batch_num == 0:
                    info = get_string('Epoch ', epoch, 'Step', batch_id + 1, 
                                      '| G loss :', loss_G.item()/self.batch_size,
                                      '| D loss (valid) : ', loss_valid.item()/self.batch_size,
                                      '| D loss (fake) : ', loss_fake.item()/self.batch_size)
                    self.record(info + '\n')

            self.save_images(img_gen.detach()[:2], prefix= 'epoch_' + str(epoch) )
            torch.save(self.model_G.state_dict(), self.save_name_G)
            torch.save(self.model_D.state_dict(), self.save_name_D)
                    

    def generate(self):
        print('Generating ... ')
        self.model_G.eval()
        vector = self.get_input_vector()
        imgs_gen = self.model_G(vector)
        self.save_images(imgs_gen)

    def save_images(self, imgs: 'image Tensor', prefix = ''): 
        num = imgs.size(0)
        for i in range(num):
            img = image_tensor_to_numpy(imgs[i])
            name = prefix + '_' + str(i) + '.png'
            path = os.path.join(self.gen_dir, name)
            cv.imwrite(path, img)

    def get_input_vector(self):
        vector = torch.normal(mean= torch.zeros(self.batch_size, self.latent_dim), 
                              std= torch.ones(self.batch_size, self.latent_dim)).to(self.device)
        return vector
