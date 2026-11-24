struct S_00125E90
{
    int pad;
    struct { int prev; int next; } e[4];
    char used[4];
    void FUN_00125e90(int a, int b);
};

// 0x00125E90
void S_00125E90::FUN_00125e90(int a, int b)
{
    e[a].next = b;
    e[b].prev = a;
    used[a] = 1;
}
