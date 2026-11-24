struct S_00032CE0
{
    int a;
    int* b;
    int FUN_00032ce0();
};

// 0x00032CE0
int S_00032CE0::FUN_00032ce0()
{
    if (a)
        return a + 2;
    if (b)
        return *b;
    return 0;
}
