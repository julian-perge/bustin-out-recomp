struct S_00124B20
{
    char pad[132];
    unsigned int bits;
    bool FUN_00124b20(int n);
};

// 0x00124B20
bool S_00124B20::FUN_00124b20(int n)
{
    return (bits & (1 << n)) ? true : false;
}
