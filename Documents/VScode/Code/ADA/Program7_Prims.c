#include <stdio.h>

int main()
{
    int n, cost[10][10], visited[10] = {0};
    int min, mincost = 0, ne = 1, a, b;

    printf("Enter number of nodes: ");
    scanf("%d", &n);

    printf("Enter cost matrix:\n");

    for(int i = 1; i <= n; i++)
    {
        for(int j = 1; j <= n; j++)
        {
            scanf("%d", &cost[i][j]);

            if(cost[i][j] == 0)
                cost[i][j] = 999;
        }
    }

    visited[1] = 1;

    while(ne < n)
    {
        min = 999;

        for(int i = 1; i <= n; i++)
        {
            if(visited[i])
            {
                for(int j = 1; j <= n; j++)
                {
                    if(!visited[j] && cost[i][j] < min)
                    {
                        min = cost[i][j];
                        a = i;
                        b = j;
                    }
                }
            }
        }

        printf("%d -> %d = %d\n", a, b, min);

        mincost += min;
        visited[b] = 1;
        ne++;

        cost[a][b] = cost[b][a] = 999;
    }

    printf("Minimum Cost = %d\n", mincost);

    return 0;
}