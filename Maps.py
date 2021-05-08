import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

weights_M  = 3
weights_N  = 3
ifmap_M = 224
ifmap_N = 224
channels = 1

def get_network_maps():
    class NN(nn.Module):
        def __init__(self):
            super(NN, self).__init__()
            self.conv1 = nn.Conv2d(3, 4, 3); 
            self.conv2 = nn.Conv2d(4, 2, 3, padding=(1,1)); 

        def forward(self, x):
            l0 = self.conv1(x)
            l1 = self.conv2(l0)
            return F.pad(l0, (1,1,1,1)).squeeze(), F.pad(l1, (1,1,1,1)).squeeze()

    ifmap = np.arange(3*ifmap_M*ifmap_N).reshape(3,ifmap_M,ifmap_N)
    weights_0 = np.arange(4*3*weights_M*weights_N).reshape(4,3,weights_M,weights_N)
    weights_1 = np.arange(2*4*weights_M*weights_N).reshape(2,4,weights_M,weights_N)

    model = NN()
    model = model.eval()
    with torch.no_grad():
        model.conv1.weight.data = torch.tensor(weights_0)
        model.conv2.weight.data = torch.tensor(weights_1)
        l0, l1 = model(torch.tensor(ifmap).unsqueeze(0))
    
    return ifmap, l0, l1, weights_0, weights_1