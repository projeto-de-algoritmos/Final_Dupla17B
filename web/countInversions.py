def countInversions(array):
    '''
    Counts the number of inversions in a given array
    Returns the sorted array and the number of inversions
    '''
    # base case
    if len(array) == 1:
        return array, 0

    else:
        # split the list into two halves
        left = array[:len(array) // 2]
        right = array[len(array) // 2:]

        # recursively sort and count both havles
        left, left_inversions = countInversions(left)
        right, right_inversions = countInversions(right)

        # sum inversions
        sorted_array = []
        i = 0
        j = 0
        inversions = 0 + left_inversions + right_inversions

    # merge and count inversions
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            sorted_array.append(left[i])
            i += 1
        else:
            sorted_array.append(right[j])
            j += 1
            inversions += (len(left) - i)
    sorted_array += left[i:]
    sorted_array += right[j:]

    return sorted_array, inversions
