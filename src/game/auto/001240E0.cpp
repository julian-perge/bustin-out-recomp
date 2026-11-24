struct S_001240e0
{
    char pad[312];
    int mode;
    char FUN_001240e0();
};

// 0x001240E0
char S_001240e0::FUN_001240e0()
{
    return mode == 2 || mode == 1;
}
