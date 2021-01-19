import cv2
import numpy as np

# get_object_length_wrt_line(): function to calculate length of an object wrt to a line represented by a and b
###############################Example########################################
# mask:
#
# 0 0 0 0 0 0 0 0 0 0
# 0 0 0 0 0 0 0 0 0 0
# 0 0 0 0 0 0 0 0 0 0
# 0 0 0 0 0 1 1 0 0 0
# 0 0 0 0 1 1 1 1 0 0
# 0 0 0 0 1 1 1 1 0 0
# 0 0 0 0 1 1 1 1 0 0
# 0 0 0 0 0 0 0 0 0 0
# 0 0 0 0 0 0 0 0 0 0
# 0 0 0 0 0 0 0 0 0 0
#
#
#line: a=0, b=5
#
# 0 0 0 0 0 0 0 0 0 0
# 0 0 0 0 0 0 0 0 0 0
# 0 0 0 0 0 0 0 0 0 0
# 0 0 0 0 0 0 0 0 0 0
# 0 0 0 0 0 0 0 0 0 0
# 0 0 0 0 0 0 0 0 0 0
# 0 0 0 0 0 0 0 0 0 0
# 0 0 0 0 0 0 0 0 0 0
# 0 0 0 0 0 0 0 0 0 0
# 1 1 1 1 1 1 1 1 1 1
#
# in this case, the distance is 2 (longest side is returned)


# a: the slope of the line (a=0 when line is horizontal, a=inf when line is vertial)
# b: the intercept of the line (y=b when line is horizontal, x=b when line is vertical)
# mask: the numpy array of the object. mask[y, x] == 1 for foreground, mask[y, x] == 0 for background
def get_object_length_wrt_line(a, b, mask):
    contours_pre, hierarchy = cv2.findContours(mask.astype('uint8'), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    max_area = -1
    max_contour = None
    for c in contours_pre:
        area = cv2.contourArea(c)
        if area > max_area:
            max_area = area
            max_contour = c
    contour = np.zeros(mask.shape)
    contour = cv2.drawContours(contour, [max_contour], -1, 1, 1)
    
    dic = {}
    
    abv_pixel = 0
    bel_pixel = 0
    
    contour_abv_cnt = 0
    contour_bel_cnt = 0
    
    flag = True
    
    for y in range(h):
        for x in range(w):
            if mask[y, x] == 1:
                
                if a == 0:
                    dist = abs(y - b)
                    if y < b:
                        flag = True
                        abv_pixel += 1
                    elif y > b:
                        flag = False
                        bel_pixel += 1
                    else:
                        continue
                        
                    if contour[y, x] == 1:
                        if flag:
                            contour_abv_cnt += 1
                        else:
                            contour_bel_cnt += 1
                        if ((b, x),flag) not in dic:
                            dic[((b, x),flag)] = [dist]
                        else:
                            dic[((b, x),flag)] += [dist]
                        
                elif a == float('inf'):
                    dist = abs(x - b)
                    if x < b:
                        flag = True
                        abv_pixel += 1
                    elif x > b:
                        flag = False
                        bel_pixel += 1
                    else:
                        continue
                        
                    if contour[y, x] == 1:
                        if flag:
                            contour_abv_cnt += 1
                        else:
                            contour_bel_cnt += 1
                        if ((y, b),flag) not in dic:
                            dic[((y, b),flag)] = [dist]
                        else:
                            dic[((y, b),flag)] += [dist]
                else:
                    ap = -1/a
                    bp = y - ap*x
                    xi = int((b-bp)/(ap-a))
                    yi = int(xi*a + b)
                    dist = np.sqrt((xi-x)**2+(yi-y)**2)
                    if y < a*x+b:
                        flag = True
                        abv_pixel += 1
                    elif y > a*x+b:
                        flag = False
                        bel_pixel += 1
                    else:
                        continue
                        
                    if contour[y, x] == 1:
                        if flag:
                            contour_abv_cnt += 1
                        else:
                            contour_bel_cnt += 1
                        if ((yi, xi),flag) not in dic:
                            dic[((yi, xi),flag)] = [dist]
                        else:
                            dic[((yi, xi),flag)] += [dist]
                            
    above = True
    if abv_pixel > bel_pixel:
        above = True
    elif bel_pixel > abv_pixel:
        above = False
    else:
        above = contour_abv_cnt >= contour_bel_cnt
    
    dists = []
    for k in dic:
        if not(k[-1]^above):
            if len(dic[k]) > 1:
                dists.append(max(dic[k]) - min(dic[k]) + 1)
            else:
                dists.append(dic[k][0])
                
    dists.sort(reverse=True)
    ratio = 4
    if len(dists) < ratio:
        return dists[0]
    else:
        sub = dists[:len(dists)//ratio]
        return sum(sub) / len(sub)