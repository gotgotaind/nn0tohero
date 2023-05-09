# https://www.youtube.com/watch?v=q8SA3rM6ckI&list=PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ&index=5

# https://github.com/karpathy/nn-zero-to-hero/blob/master/lectures/makemore/makemore_part4_backprop.ipynb
# https://www.jmlr.org/papers/volume3/bengio03a/bengio03a.pdf


import torch
import torch.nn.functional as F
#import matplotlib.pyplot as plt # for making figures



# read in all the words
words = open('../names.txt', 'r').read().splitlines()
print(f'{len(words)=}')
print(f'{max(len(w) for w in words)=}')
print(f'{words[:8]=}')




# build the vocabulary of characters and mappings to/from integers
chars = sorted(list(set(''.join(words))))
stoi = {s:i+1 for i,s in enumerate(chars)}
stoi['.'] = 0
itos = {i:s for s,i in stoi.items()}
vocab_size = len(itos)
print(f'{itos=}')
print(f'{vocab_size=}')


# build the dataset
block_size = 3 # context length: how many characters do we take to predict the next one?

def build_dataset(words):  
  X, Y = [], []
  
  for w in words:
    context = [0] * block_size
    for ch in w + '.':
      ix = stoi[ch]
      X.append(context)
      Y.append(ix)
      context = context[1:] + [ix] # crop and append

  X = torch.tensor(X)
  Y = torch.tensor(Y)
  print(f'{X.shape=}, {Y.shape=}')
  return X, Y

import random
random.seed(42)
random.shuffle(words)
n1 = int(0.8*len(words))
n2 = int(0.9*len(words))

Xtr,  Ytr  = build_dataset(words[:n1])     # 80%
Xdev, Ydev = build_dataset(words[n1:n2])   # 10%
Xte,  Yte  = build_dataset(words[n2:])     # 10%

# utility function we will use later when comparing manual gradients to PyTorch gradients
def cmp(s, dt, t):
  ex = torch.all(dt == t.grad).item()
  app = torch.allclose(dt, t.grad)
  maxdiff = (dt - t.grad).abs().max().item()
  print(f'{s:15s} | exact: {str(ex):5s} | approximate: {str(app):5s} | maxdiff: {maxdiff}')



n_embd = 10 # the dimensionality of the character embedding vectors
n_hidden = 64 # the number of neurons in the hidden layer of the MLP

g = torch.Generator().manual_seed(2147483647) # for reproducibility
C  = torch.randn((vocab_size, n_embd),            generator=g)
# Layer 1
W1 = torch.randn((n_embd * block_size, n_hidden), generator=g) * (5/3)/((n_embd * block_size)**0.5)
b1 = torch.randn(n_hidden,                        generator=g) * 0.1 # using b1 just for fun, it's useless because of BN
# Layer 2
W2 = torch.randn((n_hidden, vocab_size),          generator=g) * 0.1
b2 = torch.randn(vocab_size,                      generator=g) * 0.1
# BatchNorm parameters
bngain = torch.randn((1, n_hidden))*0.1 + 1.0
bnbias = torch.randn((1, n_hidden))*0.1

# Note: I am initializating many of these parameters in non-standard ways
# because sometimes initializating with e.g. all zeros could mask an incorrect
# implementation of the backward pass.

parameters = [C, W1, b1, W2, b2, bngain, bnbias]
print(f'{sum(p.nelement() for p in parameters)=}') # number of parameters in total
for p in parameters:
  p.requires_grad = True



batch_size = 32
n = batch_size # a shorter variable also, for convenience
# construct a minibatch
ix = torch.randint(0, Xtr.shape[0], (batch_size,), generator=g)
Xb, Yb = Xtr[ix], Ytr[ix] # batch X,Y


# forward pass, "chunkated" into smaller steps that are possible to backward one at a time

emb = C[Xb] # embed the characters into vectors
embcat = emb.view(emb.shape[0], -1) # concatenate the vectors
# Linear layer 1
hprebn = embcat @ W1 + b1 # hidden layer pre-activation
# BatchNorm layer
bnmeani = 1/n*hprebn.sum(0, keepdim=True)
bndiff = hprebn - bnmeani
bndiff2 = bndiff**2
bnvar = 1/(n-1)*(bndiff2).sum(0, keepdim=True) # note: Bessel's correction (dividing by n-1, not n)
bnvar_inv = (bnvar + 1e-5)**-0.5
bnraw = bndiff * bnvar_inv
hpreact = bngain * bnraw + bnbias
# Non-linearity
h = torch.tanh(hpreact) # hidden layer
# Linear layer 2
logits = h @ W2 + b2 # output layer
# cross entropy loss (same as F.cross_entropy(logits, Yb))
logit_maxes = logits.max(1, keepdim=True).values
norm_logits = logits - logit_maxes # subtract max for numerical stability
counts = norm_logits.exp()
counts_sum = counts.sum(1, keepdims=True)
counts_sum_inv = counts_sum**-1 # if I use (1.0 / counts_sum) instead then I can't get backprop to be bit exact...
probs = counts * counts_sum_inv
logprobs = probs.log()
loss = -logprobs[range(n), Yb].mean()

# PyTorch backward pass
for p in parameters:
  p.grad = None
for t in [logprobs, probs, counts, counts_sum, counts_sum_inv, # afaik there is no cleaner way
          norm_logits, logit_maxes, logits, h, hpreact, bnraw,
         bnvar_inv, bnvar, bndiff2, bndiff, hprebn, bnmeani,
         embcat, emb]:
  t.retain_grad()
loss.backward()
print(f'{loss=}')

dlogprobs=torch.zeros_like(logprobs)
dlogprobs[range(n),Yb]=-1.0/batch_size
dprobs=(probs**-1)*dlogprobs
dcounts=dprobs*counts_sum_inv
dcounts_sum_inv=(dprobs*counts).sum(1,keepdim=True)
dcounts_sum=dcounts_sum_inv*-1.0*counts_sum**-2
dcounts+=dcounts_sum*torch.ones_like(dcounts)
dnorm_logits=dcounts*(norm_logits.exp())
dlogits=dnorm_logits
dlogit_maxes=-1.0*dnorm_logits.sum(1,keepdim=True)
dlogits+=dlogit_maxes*(1.0*torch.nn.functional.one_hot(logits.max(1, keepdim=False).indices , num_classes=vocab_size))
db2=dlogits.sum(0)
dW2=torch.transpose(h,0,1)@dlogits
dh=dlogits@torch.transpose(W2,0,1)
dhpreact=dh*(1.0-torch.tanh(hpreact)**2)
dbngain=(dhpreact*bnraw).sum(0)
dbnraw=dhpreact*bngain
dbnbias=dhpreact.sum(0)

# bndiff2 = bndiff**2
# bnvar = 1/(n-1)*(bndiff2).sum(0, keepdim=True) # note: Bessel's correction (dividing by n-1, not n)
# bnvar_inv = (bnvar + 1e-5)**-0.5
# bnraw = bndiff * bnvar_inv
dbndiff=dbnraw*bnvar_inv.sum(0,keepdim=True)
dbnvar_inv=(bndiff*dbnraw).sum(0)
dbnvar=dbnvar_inv*-0.5*(bnvar+1e-5)**-1.5
dbndiff2=dbnvar.sum(0,keepdim=True)/(n-1)*torch.ones_like(bndiff2)
dbndiff+=dbndiff2*2.0*bndiff

# emb = C[Xb] # embed the characters into vectors
# embcat = emb.view(emb.shape[0], -1) # concatenate the vectors
# # Linear layer 1
# hprebn = embcat @ W1 + b1 # hidden layer pre-activation
# # BatchNorm layer
# bnmeani = 1/n*hprebn.sum(0, keepdim=True)
# bndiff = hprebn - bnmeani
dhprebn=dbndiff
dbnmeani=-bndiff.sum(0,keepdim=True)
print(f'{bndiff.shape=} = {hprebn.shape=} * {bnmeani.shape=}')

cmp('logprobs',dlogprobs,logprobs)
cmp('probs',dprobs,probs)
cmp('counts',dcounts,counts)
cmp('counts_sum_inv',dcounts_sum_inv,counts_sum_inv)
cmp('counts_sum',dcounts_sum,counts_sum)
cmp('dnorm_logits',dnorm_logits,norm_logits)
cmp('dlogit_maxes',dlogit_maxes,logit_maxes)
cmp('dlogits',dlogits,logits)
cmp('db2',db2,b2)
cmp('dW2',dW2,W2)
cmp('dh',dh,h)
cmp('dhpreact',dhpreact,hpreact)
cmp('dbngain',dbngain,bngain)
cmp('dbnraw',dbnraw,bnraw)
cmp('dbnbias',dbnbias,bnbias)
cmp('dbndiff',dbndiff,bndiff)
cmp('dbnvar_inv',dbnvar_inv,bnvar_inv)
cmp('dbnvar',dbnvar,bnvar)
cmp('dbndiff2',dbndiff2,bndiff2)
cmp('dhprebn',dhprebn,hprebn)
cmp('dbnmeani',dbnmeani,bnmeani)