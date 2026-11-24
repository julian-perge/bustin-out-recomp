struct S_001E42B0
{
    bool FUN_001E42B0();
};

// 0x001E42B0
// parked: source shape
bool S_001E42B0::FUN_001E42B0()
{
    return (*((unsigned char*)this - 0x560) & 1) == 1;
}
