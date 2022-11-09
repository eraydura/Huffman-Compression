import re
import math
from collections import OrderedDict
import json

"""TAKING DATA FROM FILE"""

f = open("originaltext.txt", "r")
original = f.read()
f = open("modified.txt", "r")
data = f.read()

newdata=''

# remove the punctuations
newdata = " ".join(re.split('\W+', data))
# remove digits
newdata = ''.join([i for i in newdata if not i.isdigit()])
# remove double spaces
newdata= ' '.join(newdata.split())
# make all text to uppercase
newdata= newdata.replace('i', 'İ').upper()

with open('filtered_text.txt', 'w') as f:
    f.write(newdata)

"""CALCULATING FREQUENCES"""

def Show_Freq(newdata): #count each of symbols in the text.
    freqs = dict()
    for element in newdata:
        if not element in freqs:
          freqs[element] = newdata.count(element)
    return freqs

show_with_freq = OrderedDict(sorted(Show_Freq(newdata).items(), key=lambda t: t[1]))
frequences = show_with_freq.values()
sum_freq=sum(frequences)
nodes=list(show_with_freq.items())

"""HUFFMAN CODING"""

class Huffman_Tree(object):
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

while len(nodes) > 1:
    #sort the probability first.
    nodes = sorted(nodes, key=lambda x: x[1], reverse=True)
    #pick the last 2 nodes
    (key1, c1) = nodes[-1]
    (key2, c2) = nodes[-2]
    nodes = nodes[:-2]
    #combine 2 nodes to create new one.
    node = Huffman_Tree(key1, key2)
    #add the new tree back into the collection.
    nodes.append((node, c1 + c2))

def encoding(node, string=''):
    bit = dict()
    if node in show_with_freq.keys():
        bit[node] = string
    else:
        #assign 1 for each time to right child and 0 for each time to left child.
        if (node.left):
          bit.update(encoding(node.left, string + '0'))
        if (node.right):
          bit.update(encoding(node.right, string + '1'))
    return bit

"""HUFFMAN ENCODING"""

#convert and write look table.
encoding_data = encoding(nodes[0][0])
encoded=''

for element in newdata:
    encoded += encoding_data[element]

with open('lookup.text', 'w') as f:
    str1 = json.dumps(encoding_data)
    binary = ' '.join(format(ord(letter), 'b') for letter in str1)
    f.write(binary)

with open('encoded.text', 'wb') as f:
    b = bytearray()
    # adding padding bits
    for i in range(8 - len(encoded) % 8):
        encoded += "0"
        encoded_text = "{0:08b}".format(i) + encoded
    #convert bits to byte
    for i in range(0, len(encoded_text), 8):
        b.append(int(encoded_text[i:i + 8], 2))
    f.write(bytes(b))


"""HUFFMAN DECODING"""
encoded_data=''
decoded = ''

#read lookup table
with open('lookup.text', 'r') as f:
    jsn = ''.join(chr(int(x, 2)) for x in f.read().split())
    lookup = json.loads(jsn)

with open('encoded.text','rb') as f:
    # read bits one by one
    byte = f.read(1)
    while (len(byte) > 0):
        encoded_data += bin(ord(byte))[2:].rjust(8, '0')
        byte = f.read(1)
    #delete padding bits
    encoded_data = encoded_data[8:][:-1 * int(encoded_data[:8], 2)]

element=nodes[0][0]
for bit in encoded_data:
    #opposite of the encoding.
    if bit == '1':
        element = element.right
    elif bit == '0':
        element = element.left
    #if element is in lookup value, add the element.
    if element in lookup.keys():
        decoded += element
        element = nodes[0][0]

with open('decoded.txt', 'w') as f:
    f.write(decoded)

"""COMPARASION FILES"""

original_data= len(original) * 8
modified_data= len(data) * 8
filtered_data= len(newdata) * 8
decoded_data= len(decoded) * 8

encoded_data=0
for element in encoding_data:
    encoded_data += newdata.count(element) * len(encoding_data[element])

# our total gain size from the compressed
def CR(decompressed_size,compressed_size):
    return compressed_size/decompressed_size

"""CALCULATING POSSIBILITIES & ENTROPY & EFFICINCY"""
def Show_Possiblities(data):
    possibility=dict();
    for element in data:
        possibility[element] = data[element] / sum_freq
    return possibility

def Show_bitlength(data,data2):
    bitlength = dict();
    for element in data:
        #L=∑pi*li
        bitlength[element] = data2[element]*len(data[element])
    return bitlength

def Show_entropy(data): #the average number of bits required to represent or transmit an event drawn from the probability
    entropy=dict();
    for element in data:
        # L=-∑pi*log(pi) base 2
        entropy[element] = data[element]*-math.log(data[element], 2)
    return entropy

def Efficiency(H,L): #a measure of how well a source's output
    return H/L*100

def Redundancy(H,L): #the difference between the entropy and the average length of a code
    return (L-H)*1000

#write the Entropy, efficiency, and all other relevant metrics to the text file.
symbol_with_probs = Show_Possiblities(show_with_freq)
symbol_with_bitlength = Show_bitlength(encoding_data,symbol_with_probs)
symbol_with_entropy = Show_entropy(symbol_with_probs)
evaluation=["The size of Original file: "+str(original_data)+" bytes","The size of Modified file: "+str(modified_data)+" bytes",
            "The size of Filtered file: "+str(filtered_data)+" bytes",
            "The size of Decoded file: "+str(decoded_data)+" bytes","The size of Encoded file: "+ str(encoded_data)+" bytes",
            "CR value: "+ str(CR(decoded_data,encoded_data)),"SS value: "+ str(1-CR(decoded_data,encoded_data)),
            "Frequenced: ", show_with_freq,"Sum of frequences: ", sum_freq,
            "Possibilities: ", symbol_with_probs,"LookUp Table: ", encoding_data,
            "Average Code Lengths: ", symbol_with_bitlength,"Entropies: ", symbol_with_entropy,
            "Total entropy(H): ",sum(symbol_with_entropy.values()),
            "Total Average Code Length (L): ",sum(symbol_with_bitlength.values()),
            "Efficiency: ",Efficiency(sum(symbol_with_entropy.values()),sum(symbol_with_bitlength.values())),
            "Redundancy: ",Redundancy(sum(symbol_with_entropy.values()),sum(symbol_with_bitlength.values()))]

f = open("meta.txt", "a")
for element in evaluation:
    print(element)
    f.write("\n"+str(element))
f.close()
