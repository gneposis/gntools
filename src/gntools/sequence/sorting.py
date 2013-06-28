"""
Module for manipulating sequence types.
"""

MAX_ITERATIONS = 1000

class UnjoinableListsError(Exception): pass

def joint_sort(*lists, iterations=MAX_ITERATIONS):
    """
    Returns a joint sorted list of presorted lists (or tuples).

    First it checks for common items, then it defines a gap list to put
    non-commons in. Finally it mixes them all. If items of more presorted
    list (or tuple) competes for a gap place, they will sorted in order
    of their parents were in arguments.
    """
    def sort_two(first, second):
        commons = [item for item in first if item in second]
        gap_list = [[] for i in range(len(commons)+1)]
        for l in (first, second):
            gap_item = []
            sliced = []
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
        result = []
        result.extend(gap_list[0])
        for i in range(len(commons)):
            result.append(commons[i])
            result.extend(gap_list[i+1])
        return result

    result = lists[0]
    index_set = {i for i in range(1, len(lists))}
    it = iterations
    while index_set and it > 0:
        it -= 1
        if it == 0:
            raise UnjoinableListsError('The lists at argument index {}'+
                'are unjoinable.'.format(str(index_set)))
        i = index_set.pop()
        try:
            result = sort_two(result, lists[i])
        except:
            index_set.add(i)
        
    return result

if __name__ == '__main__':
    pass
