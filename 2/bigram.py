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
#import numpy as np
import torch
torch.set_printoptions(sci_mode=False)
input='names.txt'

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

len_chars=len(charlist)

count=torch.zeros((len_chars, len_chars), dtype=torch.int32)
with open(input) as f:
    for line in (f):
        i=0
        #last_char=''
        for c in (line.lower()):

            if( c == '\n' ):
                c='.'
            if(i==0):
                prev_char='.'
            else:
                prev_char=line[i-1].lower()
            count[char_to_i[prev_char]][char_to_i[c]] += 1
            i+=1


smoothing=0
p = (count+smoothing).float()
p /= p.sum(1, keepdims=True)

# import matplotlib.pyplot as plt
# plt.figure(figsize=(16,16))
# plt.imshow(count, cmap='Blues')
# for i in range(27):
#     for j in range(27):
#         chstr = i_to_char[i] + i_to_char[j]
#         plt.text(j, i, chstr, ha="center", va="bottom", color='gray')
#         plt.text(j, i, count[i, j].item(), ha="center", va="top", color='gray')
# plt.axis('off');
# plt.savefig('image.png')
# exit()

list_chars=[]
for i in range(len_chars):
    list_chars.append(i_to_char[i])

print(f'{list_chars=}')
print(f'{p[0]=}')

import torch
import torch.nn.functional as F

g = torch.Generator().manual_seed(2147483647)
for i in range(50):
  
  out = []
  ix = char_to_i['.']
  while True:

    ix = torch.multinomial(p[ix], num_samples=1, replacement=True, generator=g).item()
    out.append(i_to_char[ix])
    if ix == char_to_i['.']:
      break
  print(''.join(out))


# compute "loss"
log_likelihood=0
n=0

with open(input) as f:
    for line in (f):
        i=0
        #last_char=''
        for c in (line.lower()):

            if( c == '\n' ):
                c='.'
            if(i==0):
                prev_char='.'
            else:
                prev_char=line[i-1].lower()
            log_likelihood += torch.log(p[char_to_i[prev_char]][char_to_i[c]])
            i+=1
            n+=1
print(f'{log_likelihood/n=}')            