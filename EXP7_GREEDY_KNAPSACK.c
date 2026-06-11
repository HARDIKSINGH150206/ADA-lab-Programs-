#include <stdio.h>

int main()
{
    float weight[50], profit[50], ratio[50];
    float capacity, totalValue = 0, temp;
    int n, i, j;

    printf("Enter number of items: ");
    scanf("%d", &n);

    for(i = 0; i < n; i++)
    {
        printf("Enter weight and profit of item %d: ", i + 1);
        scanf("%f %f", &weight[i], &profit[i]);

        ratio[i] = profit[i] / weight[i];
    }

    printf("Enter knapsack capacity: ");
    scanf("%f", &capacity);

    // Sort according to profit/weight ratio
    for(i = 0; i < n - 1; i++)
    {
        for(j = i + 1; j < n; j++)
        {
            if(ratio[i] < ratio[j])
            {
                temp = ratio[i];
                ratio[i] = ratio[j];
                ratio[j] = temp;

                temp = weight[i];
                weight[i] = weight[j];
                weight[j] = temp;

                temp = profit[i];
                profit[i] = profit[j];
                profit[j] = temp;
            }
        }
    }

    // Greedy Selection
    for(i = 0; i < n; i++)
    {
        if(weight[i] <= capacity)
        {
            totalValue += profit[i];
            capacity -= weight[i];
        }
        else
        {
            totalValue += ratio[i] * capacity;
            break;
        }
    }

    printf("Maximum Profit = %.2f\n", totalValue);

    return 0;
}