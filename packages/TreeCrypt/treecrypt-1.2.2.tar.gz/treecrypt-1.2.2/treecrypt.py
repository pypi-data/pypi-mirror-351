import random
import ast

__version__ = "1.2.2"

class Node:
    def __init__(self, x, y, index, ParentIndex):
        self.char = None
        self.left = None
        self.right = None
        self.up = None
        self.down = None
        self.index = index
        self.parentIndex = ParentIndex
        self.x = x
        self.y = y
    
    def SetChar(self, char):
        self.char = char
    
    def getArray(self):
        return [self.x, self.y, self.up, self.left, self.down, self.right, self.char, self.index, self.parentIndex]
    
class KeyMaker:
    def __init__(self, charset=None):
        if charset == None:
            self.chars = [
                'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '{', '}', '[', ']', '|', ':', ';', '"', "'", ',', '.', '?', '/'
                ]
        else:
            self.chars = charset
        self.items = [Node(0, 0, 0, None)]
        self.used = [[0, 0]]
        self.dictionary = {char: [] for char in self.chars}
    
    def GetKey(self):
        key = []
        for node in self.items:
            key.append(node.getArray())
        return key
    
    def GetDictionary(self):
        return self.dictionary
        
    def GenerateKey(self, Depth, MaxDist, MinDist=1, livePrint=False):
        def AttachLevels(self, node, level, start, MinDist, MaxDist, livePrint):
            def AttachRandom(self, AttachToNODE, MaxDist, MinDist=1, livePrint=False, tries=20):
                while True:
                    choices = ['u', 'l', 'd', 'r']
                    random.shuffle(choices)
                    dir = random.choice(choices)
                    dist = random.randrange(MinDist, MaxDist)
                    match dir:
                        case 'u':
                            x = AttachToNODE.x
                            y = AttachToNODE.y + dist
                            newUsed = []
                            for i in range(1, dist):
                                newUsed.append([AttachToNODE.x, AttachToNODE.y + i])
                        case 'l':
                            x = AttachToNODE.x - dist
                            y = AttachToNODE.y
                            newUsed = []
                            for i in range(1, dist):
                                newUsed.append([AttachToNODE.x - i, AttachToNODE.y])
                        case 'd':
                            x = AttachToNODE.x
                            y = AttachToNODE.y - dist
                            newUsed = []
                            for i in range(1, dist):
                                newUsed.append([AttachToNODE.x, AttachToNODE.y - i])
                        case 'r':
                            x = AttachToNODE.x + dist
                            y = AttachToNODE.y
                            newUsed = []
                            for i in range(1, dist):
                                newUsed.append([AttachToNODE.x + i, AttachToNODE.y])
                    flag = False
                    for node in self.items:
                        # Check if node already in place
                        if node.x == x and node.y == y:
                            flag = True
                        
                        # Check if new node passes over an old node
                        for newUsedX, newUsedY in newUsed:
                            if node.x == newUsedX and node.y == newUsedY:
                                flag = True
                    
                    for usedX, usedY in self.used:
                        # Check if an old node passes over the new node
                        if usedX == x and usedY == y:
                            flag = True
                        
                        # Check if the path of new node intersects path of an old node
                        for newUsedX, newUsedY in newUsed:
                            if usedX == newUsedX and usedY == newUsedY:
                                flag = True
                    if flag == False:
                        break
                    tries = tries - 1
                    if tries == 0:
                        return
                free = len(self.items)
                match dir:
                    case 'u':
                        AttachToNODE.up = free
                    case 'l':
                        AttachToNODE.left = free
                    case 'd':
                        AttachToNODE.down = free
                    case 'r':
                        AttachToNODE.right = free
                character = random.choice(self.chars)
                self.items.append(Node(x, y, free, AttachToNODE.index))
                self.items[free].SetChar(character)
                self.dictionary[character].append(free)
                self.used.extend(newUsed)
                if livePrint:
                    print(len(self.items))

            if start == level:
                return
            AttachRandom(self, node, MaxDist, MinDist, livePrint=livePrint)
            AttachRandom(self, node, MaxDist, MinDist, livePrint=livePrint)
            AttachRandom(self, node, MaxDist, MinDist, livePrint=livePrint)
            childNodes = [node.up, node.left, node.down, node.right]
            random.shuffle(childNodes)
            for child in childNodes:
                if child:
                    AttachLevels(self, self.items[child], level, start + 1, MinDist, MaxDist, livePrint)
        self.items = [Node(0, 0, 0, None)]
        self.used = [[0, 0]]
        self.dictionary = {char: [] for char in self.chars}
        AttachLevels(self, self.items[0], Depth, 0, MinDist, MaxDist, livePrint)
        print(f"Finished Generating key, created {len(self.items)} nodes")
    
    def Export(self, keyFile="key.txt", DictFile="dict.txt"):
        with open(keyFile, 'w', encoding='utf-8') as f:
            f.write(f"{self.GetKey()}")
            f.close()
        with open(DictFile, 'w', encoding='utf-8') as f:
            f.write(f"{self.GetDictionary()}")
            f.close()

class Crypter:
    def __init__(self):
        return
    
    def SetKey(self, key):
        self.items = []
        for nodeArray in key:
            newNode = Node(nodeArray[0], nodeArray[1], nodeArray[7], nodeArray[8])
            newNode.SetChar(nodeArray[6])
            newNode.up = nodeArray[2]
            newNode.left = nodeArray[3]
            newNode.down = nodeArray[4]
            newNode.right = nodeArray[5]
            self.items.append(newNode)
    
    def SetDictionary(self, dict):
        self.dictionary = dict

    def Import(self, keyFile="key.txt", DictFile="dict.txt"):
        with open(keyFile, 'r', encoding='utf-8') as f:
            key = ast.literal_eval(f.readline())
        with open(DictFile, 'r', encoding='utf-8') as f:
            dictionary = ast.literal_eval(f.readline())
        self.SetDictionary(dictionary)
        self.SetKey(key)

    def Decrypt(self, string):
        def decode(self, string):
            trace = list(string)
            currentNode = self.items[0]
            for i in trace:
                match i:
                    case 'u':
                        next = currentNode.up
                    case 'l':
                        next = currentNode.left
                    case 'd':
                        next = currentNode.down
                    case 'r':
                        next = currentNode.right
                currentNode = self.items[next]
            return currentNode.char
        
        words = string.split('|')
        out = ""
        for word in words:
            letters = word.split('.')
            for character in letters:
                realChar = decode(self, character)
                out = out + realChar
            out = out + " "
        out = out[:-1]
        return out
    
    def Encrypt(self, string):
        def BackTrace(self, node, str=None):
            if node.parentIndex == None:
                return str
            if str == None:
                str = ""
            parent = self.items[node.parentIndex]
            if parent.up == node.index:
                str = 'u' + str
            if parent.left == node.index:
                str = 'l' + str
            if parent.down == node.index:
                str = 'd' + str
            if parent.right == node.index:
                str = 'r' + str
            return BackTrace(self, parent, str)
        
        words = string.split(' ')
        out = ""
        for word in words:
            characters = list(word)
            for character in characters:
                trace = BackTrace(self, self.items[random.choice(self.dictionary[character])])
                out = out + trace + '.'
            out = out[:-1] + '|'
        out = out[:-1]
        return out

# Terminal Code
import argparse
parser = argparse.ArgumentParser(description="A Tree-of-Nodes based encryption algorithm")
parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')

subparsers = parser.add_subparsers(dest='mode', required=True)

# Key Generation
keygen = subparsers.add_parser('keygen', help='Generates encryption key')
keygen.add_argument("--depth", metavar=" ", help="Key generator depth",type=int, required=True)
keygen.add_argument("--min", metavar=" ", help="Minimum distance between connected nodes",type=int, default=0)
keygen.add_argument("--max", metavar=" ", help="Maximum distance between connected nodes",type=int, default=5)
keygen.add_argument("-k","--key", metavar=" ", help="File path to the key", required=True)
keygen.add_argument("-d","--dictionary", metavar=" ", help="File path to the dictionary", required=True)
keygen.add_argument("-l","--live", help="Print number of nodes as they are being generated", action="store_true", default=False)
keygen.add_argument("-c","--charset", metavar=" ", help="File path to the character set")

# Encryption
encrypt = subparsers.add_parser('encrypt', help="Encrypts raw text data")
encrypt.add_argument("-k","--key", metavar=" ", help="File path to the key", required=True)
encrypt.add_argument("-d","--dictionary", metavar=" ", help="File path to the dictionary", required=True)
enc_input = encrypt.add_mutually_exclusive_group(required=True)
enc_input.add_argument('-i', '--input', metavar=" ", help="Input string")
enc_input.add_argument('-f', '--file', metavar=" ", help="File path to input file")
encrypt.add_argument('-o', "--output", metavar=" ", help="File path to store cipher")

# Decryption
decrypt = subparsers.add_parser('decrypt', help="Decrypts cipher")
decrypt.add_argument("-k","--key", metavar=" ", help="File path to the key", required=True)
decrypt.add_argument("-d","--dictionary", metavar=" ", help="File path to the dictionary", required=True)
dec_input = decrypt.add_mutually_exclusive_group(required=True)
dec_input.add_argument('-i', '--input', metavar=" ", help="Input string")
dec_input.add_argument('-f', '--file', metavar=" ", help="File path to input file")
decrypt.add_argument('-o', "--output", metavar=" ", help="File path to store text")

args = parser.parse_args()

if args.mode == "keygen":
    if args.charset:
        with open(args.charset, 'r') as f:
            charset = ast.literal_eval(f.readline())
        newKey = KeyMaker(charset)
    else:
        newKey = KeyMaker()
    newKey.GenerateKey(args.depth, args.max, args.min, args.live)
    newKey.Export(args.key, args.dictionary)

if args.mode == "encrypt":
    crypter = Crypter()
    crypter.Import(args.key, args.dictionary)
    if args.input:
        if args.output:
            with open(args.output, 'w') as f:
                f.write(crypter.Encrypt(args.input))
        else:
            print(crypter.Encrypt(args.input))
    elif args.file:
        if args.output:
            with open(args.file, 'r') as inFile, open(args.output, 'w') as outFile:
                for line in inFile:
                    text = line.strip()
                    cipher = crypter.Encrypt(text)
                    outFile.write(cipher + "\n")
        else:
            with open(args.file, 'r') as inFile:
                for line in inFile:
                    text = line.strip()
                    cipher = crypter.Encrypt(text)
                    print(cipher)

if args.mode == "decrypt":
    crypter = Crypter()
    crypter.Import(args.key, args.dictionary)
    if args.input:
        if args.output:
            with open(args.output, 'w') as f:
                f.write(crypter.Decrypt(args.input))
        else:
            print(crypter.Decrypt(args.input))
    elif args.file:
        if args.output:
            with open(args.file, 'r') as inFile, open(args.output, 'w') as outFile:
                for line in inFile:
                    cipher = line.strip()
                    if cipher:
                        text = crypter.Decrypt(cipher)
                        outFile.write(text + "\n")
                    else:
                        outFile.write("\n")
        else:
            with open(args.file, 'r') as inFile:
                for line in inFile:
                    cipher = line.strip()
                    if cipher:
                        text = crypter.Decrypt(cipher)
                        print(text)
                    else:
                        print()