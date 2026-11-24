struct S_00124B00
{
    char pad[128];
    unsigned int bits;
    bool FUN_00124b00(int n);
};

// 0x00124B00
bool S_00124B00::FUN_00124b00(int n)
{
    return (bits & (1 << n)) ? true : false;
}
