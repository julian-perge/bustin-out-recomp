struct S_000E3A40
{
    char pad[0x14];
    char c14;
    char c15;
    char c16;
    char c17;
    char c18;
    int FUN_000e3a40();
};

// 0x000E3A40
int S_000E3A40::FUN_000e3a40()
{
    return c15 == 0 && c17 != 0;
}
