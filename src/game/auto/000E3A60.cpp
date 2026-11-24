struct S_000E3A60
{
    char pad[0x14];
    char c14;
    char c15;
    char c16;
    char c17;
    char c18;
    int FUN_000e3a60();
};

// 0x000E3A60
int S_000E3A60::FUN_000e3a60()
{
    return c15 == 0 && c18 != 0;
}
