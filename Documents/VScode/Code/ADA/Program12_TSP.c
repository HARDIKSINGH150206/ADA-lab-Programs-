#include <stdio.h>
#include <limits.h>

#define MAX 10

int n;
int dist[MAX][MAX];
int visited[MAX];
int bestPath[MAX];
int bestCost = INT_MAX;

void tsp(int currPos, int cost, int count, int path[])
{
    // Base case: all cities visited
    if(count == n)
    {
        // Add cost of returning to starting city
        cost += dist[currPos][0];

        if(cost < bestCost)
        {
            bestCost = cost;
            for(int i = 0; i < n; i++)
                bestPath[i] = path[i];
        }
        return;
    }

    // Try all unvisited cities
    for(int i = 1; i < n; i++)
    {
        if(!visited[i])
        {
            visited[i] = 1;
            path[count] = i;

            tsp(i, cost + dist[currPos][i], count + 1, path);

            visited[i] = 0;
        }
    }
}

int main()
{
    int i, j, path[MAX];

    printf("Enter number of cities: ");
    scanf("%d", &n);

    printf("Enter distance matrix:\n");
    for(i = 0; i < n; i++)
    {
        for(j = 0; j < n; j++)
        {
            scanf("%d", &dist[i][j]);
        }
    }

    visited[0] = 1;
    path[0] = 0;

    tsp(0, 0, 1, path);

    printf("\nShortest tour cost: %d\n", bestCost);

    printf("Best path: ");
    for(i = 0; i < n; i++)
        printf("%d -> ", bestPath[i]);
    printf("0\n");

    return 0;
}
