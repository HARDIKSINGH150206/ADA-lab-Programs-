#include <stdio.h>
#include <stdlib.h>

int x[20];
int count = 0;

int place(int k, int i)
{
    for(int j = 1; j < k; j++)
    {
        if(x[j] == i || abs(x[j] - i) == abs(j - k))
            return 0;
    }
    return 1;
}

void nqueen(int k, int n)
{
    for(int i = 1; i <= n; i++)
    {
        if(place(k, i))
        {
            x[k] = i;

            if(k == n)
            {
                count++;

                printf("\nSolution %d:\n", count);

                for(int row = 1; row <= n; row++)
                {
                    for(int col = 1; col <= n; col++)
                    {
                        if(x[row] == col)
                            printf("Q\t");
                        else
                            printf("-\t");
                    }
                    printf("\n");
                }
                printf("\n");
            }
            else
            {
                nqueen(k + 1, n);
            }
        }
    }
}

int main()
{
    int n;

    printf("Enter number of queens: ");
    scanf("%d", &n);

    nqueen(1, n);

    if(count == 0)
        printf("No solution found\n");
    else
        printf("Total solutions = %d\n", count);

    return 0;
}