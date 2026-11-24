struct S_00129A70
{
    int pad[6];
    struct E { int v; int p[5]; } e[8];
    void FUN_00129A70(int a, int b);
};

// 0x00129A70
void S_00129A70::FUN_00129A70(int a, int b)
{
    e[b].v = a;
}
