#include <stdio.h>

int max(int a, int b)
{
    return (a > b) ? a : b;
}

int main()
{
    int n, W;

    printf("Enter number of items: ");
    scanf("%d", &n);

    int wt[10], profit[10];

    printf("Enter weights:\n");
    for(int i = 1; i <= n; i++)
        scanf("%d", &wt[i]);

    printf("Enter profits:\n");
    for(int i = 1; i <= n; i++)
        scanf("%d", &profit[i]);

    printf("Enter knapsack capacity: ");
    scanf("%d", &W);

    int dp[10][10];

    // Build DP table
    for(int i = 0; i <= n; i++)
    {
        for(int j = 0; j <= W; j++)
        {
            if(i == 0 || j == 0)
                dp[i][j] = 0;

            else if(wt[i] <= j)
                dp[i][j] = max(dp[i-1][j],
                               profit[i] + dp[i-1][j-wt[i]]);

            else
                dp[i][j] = dp[i-1][j];
        }
    }

    // Print DP Table
    printf("\nKnapsack Table:\n");

    for(int i = 0; i <= n; i++)
    {
        for(int j = 0; j <= W; j++)
            printf("%d\t", dp[i][j]);

        printf("\n");
    }

    // Maximum Profit
    printf("\nMaximum Profit = %d\n", dp[n][W]);

    // Find selected items
    int j = W;

    printf("Selected Items: ");

    for(int i = n; i > 0; i--)
    {
        if(dp[i][j] != dp[i-1][j])
        {
            printf("%d ", i);
            j = j - wt[i];
        }
    }

    printf("\n");

    return 0;
}