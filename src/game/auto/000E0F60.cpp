struct S_000E0F60
{
    char pad[0x14];
    char c14;
    char c15;
    char c16;
    char c17;
    char c18;
    int FUN_000e0f60();
};

// 0x000E0F60
int S_000E0F60::FUN_000e0f60()
{
    return c14 == 0 && c16 != 0;
}
