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

def i_to_bigram(i):
    ii=i//len_chars
    jj=i-ii*len_chars
    #print(f'{type(i)},{type(len_chars)},{type(ii)}:{type(jj)}')
    return (i_to_char[ii],i_to_char[jj])


count=np.zeros((len_chars*len_chars,len_chars),dtype=int)
with open(input) as f:
    for line in (f):
        line=line.lower()
        i=0
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
            count[char_to_i[prev_prev_char]*len_chars+char_to_i[prev_char]][char_to_i[c]] += 1
            i+=1
            #last_char=c
        #count[char_to_i[last_char],char_to_i['.']] += 1

# add a regularisation factor to each count in order to "smooth" the probabilities
# and avoid 0 propability and get more creative?
reg=0.1
for i in range(len_chars*len_chars):
    for j in range(len_chars):
        count[i][j]+=reg


sum=np.zeros((len_chars*len_chars),dtype=int)
for i in range(len_chars*len_chars):
    for j in range(len_chars):
        sum[i]+=count[i][j]

p=np.zeros((len_chars*len_chars,len_chars),dtype=float)
for i in range(len_chars*len_chars):
#    if(sum[i]==0):
#        print(f'never found this bigram in source : {i_to_bigram(i)}')
    for j in range(len_chars):
        if(sum[i]==0):
            p[i][j]=0
        else:
            p[i][j]=count[i][j]/sum[i]

#print(p[char_to_i['.']])
#exit()
# ss=0.0
# for j in range(len_chars):
#     ss+=p[4][j]
# print(ss)
# import matplotlib.pyplot as plt
# #%matplotlib inline

# plt.figure(figsize=(32,32))
# plt.imshow(p, cmap='Blues')
# for i in range(len_chars):
#     for j in range(len_chars):
#         chstr = i_to_char[i] + i_to_char[j]
#         plt.text(j, i, chstr, ha="center", va="bottom", color='gray')
#         plt.text(j, i, p[i, j], ha="center", va="top", color='gray')
# plt.axis('off');
# plt.savefig('image.png')

my_generator = np.random.default_rng(7)
for _ in range(50):
    next_c='.'
    next_next_c='.'
    name=''
    while(True):
        next_next_i=my_generator.multinomial(1, p[char_to_i[next_c]*len_chars+char_to_i[next_next_c]]).argmax(axis=-1)
        next_c=next_next_c
        next_next_c=i_to_char[next_next_i]
        name+=next_next_c
        #print(next_c,next_i)
        if(next_next_c == '.'):
            break
    print(name)
    


log_likelihood = 0.0
n = 0


n=0
with open(input) as f:
    for line in (f):
        line=line.lower()
        i=0
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
            prob=p[char_to_i[prev_prev_char]*len_chars+char_to_i[prev_char]][char_to_i[c]] 
            logprob = np.log(prob)
            log_likelihood += logprob
            i+=1
            n+=1
print(f'{log_likelihood=}')
nll = -log_likelihood
print(f'{nll=}')
print(f'{nll/n}')