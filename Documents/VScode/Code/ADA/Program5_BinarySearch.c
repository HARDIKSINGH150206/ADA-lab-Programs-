#include <stdio.h>

int binarySearch(int a[], int low, int high, int target)
{
    while(low <= high)
    {
        int mid = low + (high - low) / 2;

        if(a[mid] == target)
            return mid;
        else if(a[mid] < target)
            low = mid + 1;
        else
            high = mid - 1;
    }

    return -1;
}

int main()
{
    int n, target, result, i, j, temp;
    int a[100];

    printf("Enter number of elements: ");
    scanf("%d", &n);

    printf("Enter %d elements in sorted order:\n", n);
    for(i = 0; i < n; i++)
        scanf("%d", &a[i]);

    // Verify array is sorted, if not sort it
    for(i = 0; i < n - 1; i++)
    {
        for(j = 0; j < n - i - 1; j++)
        {
            if(a[j] > a[j + 1])
            {
                temp = a[j];
                a[j] = a[j + 1];
                a[j + 1] = temp;
            }
        }
    }

    printf("Sorted array: ");
    for(i = 0; i < n; i++)
        printf("%d ", a[i]);
    printf("\n");

    printf("Enter element to search: ");
    scanf("%d", &target);

    result = binarySearch(a, 0, n - 1, target);

    if(result == -1)
        printf("\nElement not found in array\n");
    else
        printf("\nElement found at index: %d\n", result);

    return 0;
}
