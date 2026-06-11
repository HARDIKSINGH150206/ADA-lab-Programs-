// SELECTION SORT 


#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main()
{
    int n, a[100000], temp, min;
    int i, j;

    printf("Enter no. of elements: ");
    scanf("%d", &n);

    srand(time(NULL));

    for(i = 0; i < n; i++)
        a[i] = rand() % 10000;

    clock_t start = clock();

    for(i = 0; i < n - 1; i++)
    {
        min = i;

        for(j = i + 1; j < n; j++)
        {
            if(a[j] < a[min])
                min = j;
        }

        temp = a[i];
        a[i] = a[min];
        a[min] = temp;
    }

    clock_t end = clock();

    double time_taken = (double)(end - start) / CLOCKS_PER_SEC;

    printf("Time taken = %f seconds\n", time_taken);

    return 0;
}