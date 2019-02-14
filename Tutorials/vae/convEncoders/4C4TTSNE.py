from __future__ import print_function
import argparse
import torch
import torch.utils.data
import time
from torch import nn, optim
from torch.nn import functional as F
from torchvision import datasets, transforms
from torchvision.utils import save_image
from torchsummary import summary
from sklearn.manifold import TSNE

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import matplotlib.colors as colors

startTime = time.time()
parser = argparse.ArgumentParser(description='VAE MNIST Example')
parser.add_argument('--batch-size', type=int, default=128, metavar='N',
                    help='input batch size for training (default: 128)')
parser.add_argument('--epochs', type=int, default=10, metavar='N',
                    help='number of epochs to train (default: 10)')
parser.add_argument('--no-cuda', action='store_true', default=False,
                    help='enables CUDA training')
parser.add_argument('--seed', type=int, default=1, metavar='S',
                    help='random seed (default: 1)')
parser.add_argument('--log-interval', type=int, default=10, metavar='N',
                    help='how many batches to wait before logging training status')
parser.add_argument('--save', type=str, default='', metavar='s',
                    help='saves the weights to a given filepath')
parser.add_argument('--load', type=str, default='', metavar='l',
                    help='loads the weights from a given filepath')
parser.add_argument('--beta', type=float, default=1.0, metavar='b',
                    help='sets the value of beta for a beta-vae implementation')
parser.add_argument('--lsdim', type = int, default=2, metavar='l',
                    help='sets the number of dimensions in the latent space')
                    #current implementation may not be optimal for dims above 4
args = parser.parse_args()
args.cuda = not args.no_cuda and torch.cuda.is_available()

torch.manual_seed(args.seed)

device = torch.device("cuda" if args.cuda else "cpu")

kwargs = {'num_workers': 1, 'pin_memory': True} if args.cuda else {}
train_loader = torch.utils.data.DataLoader(
    datasets.MNIST('../data', train=True, download=True,
                   transform=transforms.ToTensor()),
    batch_size=args.batch_size, shuffle=True, **kwargs)
test_loader = torch.utils.data.DataLoader(
    datasets.MNIST('../data', train=False, transform=transforms.ToTensor()),
    batch_size=args.batch_size, shuffle=True, **kwargs)
    
"""
Secpmd Convolutional Neural Network Variational Autoencoder with Transpose Convolutional Decoder
Uses 4 convolutional hidden layers in the encoder before encoding a distribution
Applies 1 fully-connected and 3 transpose convolutional hidden layers to code before output layer.

@author Davis Jackson & Quinn Wyner
"""
    
    
class VAE(nn.Module):
    def __init__(self):
        super(VAE, self).__init__()

        #(1,28,28) -> (8,26,26)
        self.conv1 = nn.Conv2d(1, 8, 3)
        
        #(8,13,13) -> (16,12,12)
        self.conv2 = nn.Conv2d(8, 16, 2)
        
        #(16,6,6) -> (32,4,4)
        self.conv3 = nn.Conv2d(16, 32, 3)
        
        #(32,4,4) -> (64,2,2)
        self.conv4 = nn.Conv2d(32, 64, 3)

        #(80,4,4) -> lsdim mean and logvar
        self.mean = nn.Linear(64*2*2, args.lsdim)
        self.variance = nn.Linear(64*2*2, args.lsdim)

        #(2 -> 4)
        self.fc1 = nn.Linear(args.lsdim, 4)
        #reshape elsewhere
        
        #(1,2,2) -> (32,7,7)
        self.convt1 = nn.ConvTranspose2d(1, 32, 6)
        
        #(32,7,7) -> (16, 14, 14)
        self.convt2 = nn.ConvTranspose2d(32, 16, 8)

        #(16, 14, 14) -> (8, 20, 20)
        self.convt3 = nn.ConvTranspose2d(16, 8, 7)

        #(8,20, 20) -> (1, 28, 28) 
        self.convt4 = nn.ConvTranspose2d(8, 1, 9)
        

    def encode(self, x):
        return self.mean(x), self.variance(x)

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5*logvar)
        eps = torch.randn_like(std)
        return eps.mul(std).add_(mu)

    def decode(self, z):
        #implement
        d1 = F.relu(self.fc1(z))
        d1r = d1.view(-1,1,2,2)
        d2 = F.relu(self.convt1(d1r))
        d3 = F.relu(self.convt2(d2))
        d4 = F.relu(self.convt3(d3))
        d5 = F.relu(self.convt4(d4))
        return d5
        

    def forward(self, x):
        #(1,28,28) -> (8,26,26) -> (8,13,13)
        x = F.max_pool2d(F.relu(self.conv1(x)), (2,2))
        
        #(8,13,13) -> (16,12,12) -> (16,6,6)
        x = F.max_pool2d(F.relu(self.conv2(x)), (2,2))
        
        #(16,6,6) -> (32,4,4)
        x = F.relu(self.conv3(x))
        
        #(32,4,4) -> (64,2,2)
        x = F.relu(self.conv4(x))

        #(64,2,2) -> lsdim mean and logvar
        mu, logvar = self.encode(x.view(-1, 64*2*2))

        #get code
        z = self.reparameterize(mu, logvar)

        #decode code
        return self.decode(z), mu, logvar, z


model = VAE().to(device)
optimizer = optim.Adam(model.parameters(), lr=1e-3)


# Reconstruction + KL divergence losses summed over all elements and batch
def loss_function(recon_x, x, mu, logvar):
    MSE = F.mse_loss(recon_x.view(-1,784), x.view(-1, 784), reduction = 'sum')

    # see Appendix B from VAE paper:
    # Kingma and Welling. Auto-Encoding Variational Bayes. ICLR, 2014
    # https://arxiv.org/abs/1312.6114
    # 0.5 * sum(1 + log(sigma^2) - mu^2 - sigma^2)
    KLD = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())

    return MSE + args.beta*KLD


def train(epoch):
    model.train()
    train_loss = 0
    for batch_idx, (data, _) in enumerate(train_loader):
        data = data.to(device)
        optimizer.zero_grad()
        recon_batch, mu, logvar, z = model(data)
        loss = loss_function(recon_batch, data, mu, logvar)
        loss.backward()
        train_loss += loss.item()
        optimizer.step()
        if batch_idx % args.log_interval == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader),
                loss.item() / len(data)))

    print('====> Epoch: {} Average loss: {:.4f}'.format(
          epoch, train_loss / len(train_loader.dataset)))


def test(epoch, max, startTime):
    model.eval()
    test_loss = 0
    zTensor = torch.empty(0,args.lsdim).to(device)
    labelTensor = torch.empty(0, dtype = torch.long)
    with torch.no_grad():
        for i, (data, _) in enumerate(test_loader):
            data = data.to(device)
            recon_batch, mu, logvar, z = model(data)
            test_loss += loss_function(recon_batch, data, mu, logvar).item()
            zTensor = torch.cat((zTensor, z), 0)
            labelTensor = torch.cat((labelTensor, _), 0)
   
    test_loss /= len(test_loader.dataset)
    print('====> Test set loss: {:.4f}'.format(test_loss))
    if(epoch == max):
        print("--- %s seconds ---" % (time.time() - startTime))
        Z_embedded = TSNE(n_components=2, verbose=1).fit_transform(zTensor.cpu())
        print(Z_embedded.shape)
        
        z1 = Z_embedded[:, 0]
        z2 = Z_embedded[:, 1]
        cmap = colors.ListedColormap(['#e6194B', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#42d4f4', '#f032e6', '#bfef45', '#fabebe'])
        scatterPlot = plt.scatter(z1, z2, s = 4, c = labelTensor, cmap = cmap)
        plt.colorbar()
        plt.show()
         
def dplot(x):
    img = decode(x)
    plt.imshow(img)

if __name__ == "__main__":
    summary(model,(1,28,28))
    if(args.load == ''):
        for epoch in range(1, args.epochs + 1):
            train(epoch)
            test(epoch, args.epochs, startTime)
    else:
        model.load_state_dict(torch.load(args.load))
        test(args.epochs, args.epochs, startTime)
    if(args.save != ''):
        torch.save(model.state_dict(), args.save)