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
# def i_to_char(i):
#     return i_to_char[i]

# def char_to_i(char):
#     return char_to_i[char]

def onehot_to_char(enc):
    return (i_to_char[torch.argmax(enc[i][0]).item()],i_to_char[torch.argmax(enc[i][1]).item()])
                     
len_chars=len(charlist)

def i_to_bigram(i):
    ii=i//len_chars
    jj=i-ii*len_chars
    #print(f'{type(i)},{type(len_chars)},{type(ii)}:{type(jj)}')
    return (i_to_char[ii],i_to_char[jj])

#count=np.zeros((len_chars,len_chars),dtype=int)
xs=[]
ys=[]
prevc='.'
total_samples=0
lines_parsed=0
        
with open(input) as f:
    for line in (f):
        line=line.lower()
        i=0
        lines_parsed+=1
        #if(lines_parsed>3):
        #    break
        #last_char=''
        for c in (line.lower()):

            if( c == '\n' ):
                c='.'
            if(i==0):
                prev_char='.'
                prev_prev_char='.'
            elif(i==1):
                prev_char=line[i-1]
                prev_prev_char='.'
            else:
                prev_char=line[i-1]
                prev_prev_char=line[i-2]
            xs.append([char_to_i[prev_prev_char],char_to_i[prev_char]])
            ys.append([char_to_i[prev_char],char_to_i[c]])
            total_samples+=1

            #count[char_to_i[prev_prev_char]*len_chars+char_to_i[prev_char]][char_to_i[c]] += 1
            i+=1
print(f'{total_samples=}')
print(f'{len_chars=}')
xs=torch.tensor(xs)
ys=torch.tensor(ys)

g = torch.Generator().manual_seed(2147483647)
W = torch.randn((len_chars, len_chars), generator=g,requires_grad=True)
xenc = F.one_hot(xs, num_classes=len_chars).float()
#print(xenc[1])
#exit()

# gradient descent
for k in range(5):

    logits = xenc @ W # predict log-counts


    #print(f'{logits.size()}')
    #print(f'{logits[torch.arange(total_samples),0, ys[:,1]]=}')
    counts = logits.exp() # counts, equivalent to N
    probs = counts / counts.sum(2, keepdims=True) # probabilities for next character
    #print(f'{probs[0]}')
    loss0 = -probs[torch.arange(total_samples),0, ys[:,0]].log().mean()
    loss1 = -probs[torch.arange(total_samples),1, ys[:,1]].log().mean()
    # print(f'{W.size()=}')
    # print(f'{xenc.size()=}')
    # print(f'{logits.size()=}')
    # print(f'{counts.size()=}')
    # print(f'{loss0.size()=}')
    # print(f'{probs[5,0,:].sum()=}')
    # print(f'{probs[5,1,:].sum()=}')
    #exit()
    loss=(loss0+loss1)/2
    for i in range(0):
        print(f'{onehot_to_char(xenc)=},{i_to_char[ys[i,0].item()]=},{i_to_char[ys[i,1].item()]=}')

    print(f'{loss.item()=}')

    # backward pass
    W.grad = None # set to zero the gradient
    loss.backward()

    # update
    W.data += -5 * W.grad



#print(probs.shape)
#print(len_chars)


for i in range(50):
  
  out = []
  ix = [char_to_i['.'],char_to_i['.']]
  while True:
    
    # ----------
    # BEFORE:
    #p = P[ix]
    # ----------
    # NOW:
    xenc = F.one_hot(torch.tensor(ix), num_classes=len_chars).float()
    logits = xenc @ W # predict log-counts
    counts = logits.exp() # counts, equivalent to N

    p = counts / counts.sum(1, keepdims=True) # probabilities for next character
    print(f'{p.size()=}')
    print(f'{p.sum(dim=1)=}')
    exit()
    # ----------
    
    ix1 = torch.multinomial(p[0,0,:], num_samples=1, replacement=True, generator=g).item()
    ix2 = torch.multinomial(p[0,1,:], num_samples=1, replacement=True, generator=g).item()
    print(f'{size(ix1)}')
    exit()
    ix=[ix1,ix2]
    #ix1 = torch.multinomial(p[:,1], num_samples=1, replacement=True, generator=g).item()
    out.append(i_to_char[ix1])
    if ix1 == char_to_i['.']:
      break
    #ix=[ix0,ix1]
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
    