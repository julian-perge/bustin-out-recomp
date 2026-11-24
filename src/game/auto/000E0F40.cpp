struct S_000E0F40
{
    char pad[0x14];
    char c14;
    char c15;
    char c16;
    char c17;
    char c18;
    int FUN_000e0f40();
};

// 0x000E0F40
int S_000E0F40::FUN_000e0f40()
{
    return c14 == 0 && c15 != 0;
}
