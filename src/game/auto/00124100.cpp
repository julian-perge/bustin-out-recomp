struct S_00124100
{
    char pad[308];
    int mode;
    char FUN_00124100();
};

// 0x00124100
char S_00124100::FUN_00124100()
{
    return mode == 2 || mode == 1;
}
