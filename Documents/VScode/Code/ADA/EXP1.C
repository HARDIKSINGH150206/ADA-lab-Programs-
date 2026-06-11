#include <stdio.h>

int main() {
    int n, cost[10][10], parent[10] = {0};
    int min, mincost = 0, ne = 1, a, b, u, v;

    printf("Enter number of nodes: ");
    scanf("%d", &n);

    printf("Enter cost matrix:\n");
    for(int i = 1; i <= n; i++)
        for(int j = 1; j <= n; j++) {
            scanf("%d", &cost[i][j]);
            if(cost[i][j] == 0) cost[i][j] = 999;
        }

    while(ne < n) {
        min = 999;

        for(int i = 1; i <= n; i++)
            for(int j = 1; j <= n; j++)
                if(cost[i][j] < min) {
                    min = cost[i][j];
                    a = u = i;
                    b = v = j;
                }

        while(parent[u]) u = parent[u];
        while(parent[v]) v = parent[v];

        if(u != v) {
            printf("%d -> %d = %d\n", a, b, min);
            mincost += min;
            parent[v] = u;
            ne++;
        }

        cost[a][b] = cost[b][a] = 999;
    }

    printf("Minimum Cost = %d", mincost);
    return 0;
}