#include <stdio.h>

int count = 0;

void subset(int sum, int k, int n, int set[], int x[], int target)
{
    if(sum == target)
    {
        printf("Subset %d: ", ++count);

        for(int i = 0; i < n; i++)
        {
            if(x[i] == 1)
                printf("%d ", set[i]);
        }

        printf("\n");
        return;
    }

    if(k == n || sum > target)
        return;

    // Include current element
    x[k] = 1;
    subset(sum + set[k], k + 1, n, set, x, target);

    // Exclude current element
    x[k] = 0;
    subset(sum, k + 1, n, set, x, target);
}

int main()
{
    int n, target;

    printf("Enter number of elements: ");
    scanf("%d", &n);

    int set[20], x[20] = {0};

    printf("Enter elements:\n");
    for(int i = 0; i < n; i++)
        scanf("%d", &set[i]);

    printf("Enter target sum: ");
    scanf("%d", &target);

    subset(0, 0, n, set, x, target);

    if(count == 0)
        printf("Subset not possible!\n");

    return 0;
}
