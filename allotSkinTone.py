# Five color samples from dark to light (1: dark :: 5: whitest)
# 1 :: ( 59 , 34 , 25 ) 
# 2 :: ( 161 , 110 , 75 )
# 3 :: ( 212 , 170 , 120 ) 
# 4 :: ( 230 , 188 , 152 )
# 5 :: ( 255 , 231 , 209 )

# Palette One
# 0 :: ( 59, 34, 25 )       - Dark 
# 1 :: ( 161 , 110 , 75 )   - Mid brown
# 2 :: ( 230 , 188 , 152 )  - Fair 

# Palette Two
# 0 :: ( 59, 34, 25 )       - Dark 
# 1 :: ( 212 , 170 , 120 )  - Mid brown
# 2 :: ( 255 , 231 , 209 )  - Fair 

# Palette Three
# 0 :: ( 59, 34, 25 )       - Dark 
# 1 :: ( 186, 140, 97 )     - Mid brown
# 2 :: ( 255 , 231 , 209 )  - Fair 

# Palette Four
# 0 :: ( 59, 34, 25 )       - Dark 
# 1 :: ( 186, 128, 97 )     - Mid brown
# 2 :: ( 255 , 231 , 209 )  - Fair 

def allotSkin(colorsList):
    
    colors = [
        [59, 34, 25],
        [161 , 110 , 75],
        [230 , 188 , 152]
    ]

    diffList = []
    for i in range(3):
        diff = diffColor(colorsList, colors[i])
        diffList.append(diff)
        # list.append(elem)
    
    indexOfMinDist = diffList.index(min(diffList))
    # print(colors[indexOfMinDist])
    # label = "Dark" if (indexOfMinDist == 0) else "Mid Brown" if (indexOfMinDist == 1) else "Fair"
    return indexOfMinDist
    # allotedSkinTone = colors[indexOfMinDist]
    # return allotedSkinTone


def diffColor(colorsList,colorX):
    x1 = abs(colorsList[0]-colorX[0])
    x2 = abs(colorsList[1]-colorX[1])
    x3 = abs(colorsList[2]-colorX[2])
    x = int(x1+x2+x3)
    return x
