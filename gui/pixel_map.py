"""
   SR0         SR1        SR2
 ________   ________   ________
|00000000| |00000000| |00000000|
 |      |   |      |   |      |
 22     12  24     14  1      11  
"""

def _bin(value):
    r = ''
    while (value != 0x00):
        r = str(value & 0x01) + r
        value = value >> 1
    return r

"""
Create a map for each pixel
24 bits for each address
    16 for anodes (columns) - RG
    8 for cathodes (rows)
"""
def make_map(width=8, height=8):
    pmap = [ [ [0, [0, 0]] for i in range(8) ] for i in range(8) ]

    for row in range(8):
        catode_byte = ~(0x01 << row) & 0xFF
        for col in range(8):
            red = (0x000100 << col*2+1) & 0xFFFFFF
            green = (0x000100 << col*2) & 0xFFFFFF
            pmap[row][col][0] = red ^ catode_byte
            pmap[row][col][1] = green ^ catode_byte
    return pmap

def frame2addr(pmap, frame):
    frame = frame.replace(' ', '')
    pixels = []
    for ci, c in enumerate(frame):
        row = (ci)/8
        col = (ci)%8
        if c == 'r':
            pixels.append(pmap[row][col][0])
        elif c == 'g':
            pixels.append(pmap[row][col][1])
        elif c == 'o':
            pixels.append(pmap[row][col][0])
            pixels.append(pmap[row][col][1])
        else:
            continue
    return pixels

def print_map(pmap):
    out = 'Arduino: long pmap[8][8][2] = {\n'
    for ri, r in enumerate(pmap):
        if ri > 0:
            out = out + ', \n'
        out = out + '\t{'
        for ci, c in enumerate(r):
            if ci > 0:
                out = out + ', '
            out = out + '{'
            out = out + '0x%x, 0x%x' % (c[0], c[1])
            out = out + '}'
        out = out + '}'
    out = out + '\n}'
    print out


    out = 'Python: pmap = [\n'
    for ri, r in enumerate(pmap):
        if ri > 0:
            out = out + ', \n'
        out = out + '\t['
        for ci, c in enumerate(r):
            if ci > 0:
                out = out + ', '
            out = out + '['
            out = out + '0x%x, 0x%x' % (c[0], c[1])
            out = out + ']'
        out = out + ']'
    out = out + '\n]'
    print out

def rotate90(frame):
    frame = frame.replace(' ', '')
    pixels = [[0]*8 for i in range(8)]
    for ci, c in enumerate(frame):
        pixels[(ci)/8][(ci)%8] = c
    rotated = zip(*pixels[::-1])
    return ''.join([''.join(r) for r in rotated])



f0 = '* * * r r * * *'\
     '* * r * * r * *'\
     '* r * * * * r *'\
     'r r * r r * r r'\
     '* r * r r * r *'\
     '* r * * * * r *'\
     '* r * r * * r *'\
     '* r * r * * r *'


f0 = 'o * * * * * * *'\
     '* * r * * r * *'\
     '* * * * * * * *'\
     '* * * r r * * *'\
     '* r * * * * r *'\
     '* r * * * * r *'\
     '* * r r r r * *'\
     '* * * * * * * o'




pmap = make_map()
print_map(pmap)

print 'f0:'
print ', '.join([hex(p) for p in frame2addr(pmap, f0)])


print 'rotated f0:'
print ', '.join([hex(p) for p in frame2addr(pmap, rotate90(rotate90(f0)))])
#print _bin(pmap[0][0][0])



print frame2addr(pmap, f0)
