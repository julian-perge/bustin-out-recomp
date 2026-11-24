struct S_00035B20
{
    char pad[0xa4];
    int state;
    bool FUN_00035B20();
};

// 0x00035B20
bool S_00035B20::FUN_00035B20()
{
    return state == 3 || state == 5;
}
