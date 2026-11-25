struct S_000A42C0
{
    char pad[0x16bc];
    int a;
    int b;
    char pad2[8];
    int c;
    void FUN_000a42c0(int x);
};

// 0x000A42C0
void S_000A42C0::FUN_000a42c0(int x)
{
    a = x;
    c = b - x;
}
