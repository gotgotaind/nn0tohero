"""
https://www.youtube.com/watch?v=PaCmpygFfXo&list=PLAqhIrjkxbuWI23v9cThsA9GvCAUhRvKZ&index=2

https://github.com/karpathy/makemore
https://github.com/karpathy/nn-zero-to-hero/blob/master/lectures/makemore/makemore_part1_bigrams.ipynb


Exercises:
E01: train a trigram language model, i.e. take two characters as an input to predict the 3rd one. Feel free to use either counting or a neural net. Evaluate the loss; Did it improve over a bigram model?
E02: split up the dataset randomly into 80% train set, 10% dev set, 10% test set. Train the bigram and trigram models only on the training set. Evaluate them on dev and test splits. What can you see?
E03: use the dev set to tune the strength of smoothing (or regularization) for the trigram model - i.e. try many possibilities and see which one works best based on the dev set loss. What patterns can you see in the train and dev set loss as you tune this strength? Take the best setting of the smoothing and evaluate on the test set once and at the end. How good of a loss do you achieve?
E04: we saw that our 1-hot vectors merely select a row of W, so producing these vectors explicitly feels wasteful. Can you delete our use of F.one_hot in favor of simply indexing into rows of W?
E05: look up and use F.cross_entropy instead. You should achieve the same result. Can you think of why we'd prefer to use F.cross_entropy instead?
E06: meta-exercise! Think of a fun/interesting exercise and complete it.

 """
import numpy as np
import torch.nn.functional as F
import torch


input='prenoms.txt'

# Generate the list of charaters
charset=set()

with open(input) as f:
    for i,line in enumerate(f):
        for c in line:
            #charset.add(char.lower)
            if( c == '\n' ):
                c='.'
            charset.add(c.lower())

charlist=list(charset)
charlist.sort()

char_to_i=dict()
i_to_char=dict()


for i,c in enumerate(charlist):
    char_to_i[c]=i
    i_to_char[i]=c

#print(char_to_i)

len_chars=len(charlist)



#count=np.zeros((len_chars,len_chars),dtype=int)
xs=[]
ys=[]
prevc='.'
total_chars=0

with open(input) as f:
    i=0
    for line in (f):

        #last_char=''
        for c in (line.lower()):

            if( c == '\n' ):
                c='.'
            xs.append(char_to_i[prevc])
            ys.append(char_to_i[c])
            prevc=c
            total_chars+=1
        i+=1
        
#        if(i > 2):
#            break
            #last_char=c
        #count[char_to_i[last_char],char_to_i['.']] += 1
#for i,x in enumerate(xs):
    #print(i_to_char[x],i_to_char[ys[i]])

xs=torch.tensor(xs)
ys=torch.tensor(ys)

g = torch.Generator().manual_seed(2147483647)
W = torch.randn((len_chars, len_chars), generator=g,requires_grad=True)
xenc = F.one_hot(xs, num_classes=len_chars).float()
print(f'{xenc.size()=},{total_chars}')

# initialize those so that they are in global scope and 
# and I can use them at the end of gradient descent
logits = xenc @ W # predict log-counts
counts = logits.exp() # counts, equivalent to N
probs = counts / counts.sum(1, keepdims=True) # probabilities for next character
# gradient descent
for k in range(50):

    logits = xenc @ W # predict log-counts
    counts = logits.exp() # counts, equivalent to N
    probs = counts / counts.sum(1, keepdims=True) # probabilities for next character
    loss = -probs[torch.arange(total_chars), ys].log().mean()+ 0.01*(W**2).mean()
    print(loss.item())
    # backward pass
    W.grad = None # set to zero the gradient
    loss.backward()

    # update
    W.data += -50 * W.grad



#print(probs.shape)
#print(len_chars)
list_chars=[]
for i in range(len_chars):
    list_chars.append(i_to_char[i])
print(f'{list_chars=}')
print(f'{probs[0]}')

for i in range(total_chars):
    if(xs[i]==0):
        print(f'{xs[i]=},{ys[i]=}')

for i in range(10):
  
  out = []
  ix = char_to_i['.']
  while True:    
    ix = torch.multinomial(probs[ix], num_samples=1, replacement=True, generator=g).item()
    out.append(i_to_char[ix])
    if ix == char_to_i['.']:
      break
  print(''.join(out))

exit()




my_generator = np.random.default_rng(7)
for _ in range(50):
    next_c='.'
    name=''
    while(True):
        next_i=my_generator.multinomial(1, p[char_to_i[next_c]]).argmax(axis=-1)
        next_c=i_to_char[next_i]
        name+=next_c
        #print(next_c,next_i)
        if(next_c == '.'):
            break
    print(name)
    