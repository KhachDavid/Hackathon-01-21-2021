from .Song import Song_by

# Credit: https://www.geeksforgeeks.org/quick-sort/

def partition(arr, low, high, element):
    i = (low - 1)  # index of smaller element
    pivot = arr[high]  # pivot

    for j in range(low, high):
        # If current element is smaller than or
        # equal to pivot
        class_method = getattr(Song_by, "get_" + element)
        if class_method(arr[j]) <= class_method(pivot):
            # increment index of smaller element
            i = i + 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


# The main function that implements QuickSort
# arr[] --> Array to be sorted,
# low  --> Starting index,
# high  --> Ending index

# Function to do Quick sort


def quick_sort(arr, low, high, element):
    if len(arr) == 1:
        return arr
    if low < high:
        # pi is partitioning index, arr[p] is now
        # at right place
        pi = partition(arr, low, high, element)

        # Separately sort elements before
        # partition and after partition
        quick_sort(arr, low, pi - 1, element)
        quick_sort(arr, pi + 1, high, element)