struct S_001A5890
{
    int a;
    int b;
    S_001A5890 *FUN_001a5890();
};

// The unit holds 5 trailing bytes (66 8B 41 5E C3) at 0x001A58A0 after the function; their start is missing (F-0135).
// 0x001A5890
// parked: unclassified
S_001A5890 *S_001A5890::FUN_001a5890()
{
    a = 0;
    b = 0;
    return this;
}
