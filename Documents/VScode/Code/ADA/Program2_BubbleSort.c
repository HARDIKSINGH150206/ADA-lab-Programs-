#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main()
{
    int n, i, j, temp;
    int a[10000];

    printf("Enter number of elements: ");
    scanf("%d", &n);

    srand(time(NULL));

    for(i = 0; i < n; i++)
        a[i] = rand() % 1000;

    printf("Original array (first 20 elements): \n");
    for(i = 0; i < (n < 20 ? n : 20); i++)
        printf("%d ", a[i]);
    printf("\n");

    clock_t start = clock();

    // Bubble Sort
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

    clock_t end = clock();
    double time_taken = (double)(end - start) / CLOCKS_PER_SEC;

    printf("\nSorted array (first 20 elements): \n");
    for(i = 0; i < (n < 20 ? n : 20); i++)
        printf("%d ", a[i]);
    printf("\n");

    printf("\nTime taken: %f seconds\n", time_taken);

    return 0;
}
