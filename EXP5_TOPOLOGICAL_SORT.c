#include <stdio.h>

int main()
{
    int n, a[10][10], indegree[10] = {0};
    int count = 0;

    printf("Enter number of vertices: ");
    scanf("%d", &n);

    printf("Enter adjacency matrix:\n");

    for(int i = 0; i < n; i++)
    {
        for(int j = 0; j < n; j++)
        {
            scanf("%d", &a[i][j]);
        }
    }

    // Calculate indegree of each vertex
    for(int j = 0; j < n; j++)
    {
        for(int i = 0; i < n; i++)
        {
            indegree[j] += a[i][j];
        }
    }

    printf("Topological Order: ");

    while(count < n)
    {
        for(int i = 0; i < n; i++)
        {
            if(indegree[i] == 0)
            {
                printf("%d ", i);

                indegree[i] = -1;   // mark as processed
                count++;

                for(int j = 0; j < n; j++)
                {
                    if(a[i][j] == 1)
                        indegree[j]--;
                }
            }
        }
    }

    return 0;
}