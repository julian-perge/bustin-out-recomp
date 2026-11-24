struct S_000E61B0
{
    char pad[0x7d];
    char a;
    char pad2[0x32];
    char b;
    void FUN_000e61b0();
};

// 0x000E61B0
void S_000E61B0::FUN_000e61b0()
{
    if (a && !b)
        b = 1;
}
