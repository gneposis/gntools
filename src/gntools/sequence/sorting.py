"""
Module for manipulating sequence types.
"""

def joint_sort(*lists):
    """
    Returns a joint sorted list of presorted lists (or tuples).

    First it checks for common items, then it defines a gap list to put
    non-commons in. Finally it mixes them all. If items of more presorted
    list (or tuple) competes for a gap place, they will sorted in order
    of their parents were in arguments.
    """
    commons = lists[0]
    for l in lists:
        commons = [item for item in commons if item in l]

    gap_list = [[] for i in range(len(commons)+1)]

    for i, l in enumerate(lists):
        gap_item = list()
        sliced = list()
        for common_item in commons:
            common_i = l.index(common_item)
            sliced.append((list(l[:common_i]), list(l[common_i+1:])))

        gap_item.append(sliced[0][0])                     
        for j in range(len(sliced) - 1):
            gap_item.append([item for item in sliced[j][1]
                                if item in sliced[j+1][0]])
        gap_item.append(sliced[-1][1])

        for j, item in enumerate(gap_item):  
            gap_list[j].extend([i for i in item if i not in commons])

    result = list()
    result.extend(gap_list[0])
    for i in range(len(commons)):
        result.append(commons[i])
        result.extend(gap_list[i+1])
    return result

if __name__ == '__main__':
    pass
