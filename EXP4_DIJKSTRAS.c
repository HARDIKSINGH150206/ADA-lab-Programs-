#include <stdio.h>

int main()
{
    int n, dist[10], cost[10][10], visited[10] = {0};
    int source, min, u;

    printf("Enter number of vertices: ");
    scanf("%d", &n);

    printf("Enter cost matrix:\n");

    for(int i = 0; i < n; i++)
    {
        for(int j = 0; j < n; j++)
        {
            scanf("%d", &cost[i][j]);

            if(cost[i][j] == 0 && i != j)
                cost[i][j] = 999;
        }
    }

    printf("Enter source vertex: ");
    scanf("%d", &source);

    for(int i = 0; i < n; i++)
        dist[i] = cost[source][i];

    visited[source] = 1;
    dist[source] = 0;

    for(int count = 1; count < n; count++)
    {
        min = 999;

        for(int i = 0; i < n; i++)
        {
            if(!visited[i] && dist[i] < min)
            {
                min = dist[i];
                u = i;
            }
        }

        visited[u] = 1;

        for(int i = 0; i < n; i++)
        {
            if(!visited[i] && dist[u] + cost[u][i] < dist[i])
            {
                dist[i] = dist[u] + cost[u][i];
            }
        }
    }

    printf("\nShortest paths from source %d:\n", source);

    for(int i = 0; i < n; i++)
    {
        printf("%d --> %d = %d\n", source, i, dist[i]);
    }

    return 0;
}