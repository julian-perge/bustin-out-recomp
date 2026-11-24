struct S_00128bd0
{
    char pad[0x270];
    int mode;
    int FUN_00128bd0();
};

// 0x00128BD0
int S_00128bd0::FUN_00128bd0()
{
    switch (mode) {
    case 2:
        return 0x11;
    default:
        return 0x2222;
    }
}
