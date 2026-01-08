##takes in two sorted list which might have different length. 

def merge(l1, l2): #merges two list into one with linear time
    sorted = []

    i1 = 0
    i2 = 0

    while i1 < len(l1) or i2 < len(l2):
        if i1 == len(l1):
            sorted.append(l2[i2])
            i2 += 1
        elif i2 == len(l2):
            sorted.append(l1[i1])
            i1 += 1
        elif l1[i1] <= l2[i2]:
            sorted.append(l1[i1])
            i1 += 1
        else:
            sorted.append(l2[i2])
            i2 += 1
    return sorted



def merge_sort(l: list):
    if len(l) <= 1:
        return l
    
    a = merge_sort(l[:len(l)//2])
    b = merge_sort(l[len(l)//2:])

    return merge(a, b)

    #O(nlogn) is the time complexity


l = [12, -54, 315, -87, -98, -99, 135, 125, 3, 0, 54]
print(merge_sort(l))
