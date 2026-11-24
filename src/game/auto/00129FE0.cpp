struct S_00129FE0
{
    char pad[0x58];
    int v[16];
    void FUN_00129fe0(int a, int b);
};

// 0x00129FE0
void S_00129FE0::FUN_00129fe0(int a, int b)
{
    v[a * 2 + b] = -v[a * 2 + b];
}
