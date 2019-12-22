import numpy as np
import pygame as pg
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torch.nn.functional as F

from vicero.algorithms.reinforce import Reinforce
from ris import Ris

cell_size  = 32
env = Ris(cell_size, height=10, width=5)

def plot(history):
        plt.figure(2)
        plt.clf()
        durations_t = torch.FloatTensor(history)
        plt.title('Training...')
        plt.xlabel('Episode')
        plt.ylabel('Duration')
        plt.plot(durations_t.numpy(), c='lightgray', linewidth=1)

        if len(durations_t) >= 100:
            means = durations_t.unfold(0, 100, 1).mean(1).view(-1)
            means = torch.cat((torch.zeros(99), means))
            plt.plot(means.numpy(), c='green')
            
        plt.pause(0.001)

pg.init()
screen = pg.display.set_mode((cell_size * len(env.board[0]), cell_size * len(env.board)))
env.screen = screen

class PolicyNet(nn.Module):
    def __init__(self):
        super(PolicyNet, self).__init__()
        self.conv = nn.Conv2d(3, 8, 3, padding=1)
        self.conv2 = nn.Conv2d(8, 4, 3)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(96, 24)
        self.fc2 = nn.Linear(24, 10)
        self.fc3 = nn.Linear(10, 5)

    def forward(self, x):
        x = F.relu(self.conv(x))
        #x = self.pool(x)
        x = F.relu(self.conv2(x))
        x = torch.flatten(x)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = torch.sigmoid(self.fc3(x))
        return x

"""
class PolicyNet(nn.Module):
    def __init__(self):
        super(PolicyNet, self).__init__()
        self.conv = nn.Conv2d(3, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 8, 3)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(192, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 5)

    def forward(self, x):
        x = F.relu(self.conv(x))
        #x = self.pool(x)
        x = F.relu(self.conv2(x))
        x = torch.flatten(x)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = torch.sigmoid(self.fc3(x))
        return x
"""

poligrad = Reinforce(env, polinet=PolicyNet(), learning_rate=0.004, gamma=0.98, batch_size=5, plotter=plot)
poligrad.train(10000)