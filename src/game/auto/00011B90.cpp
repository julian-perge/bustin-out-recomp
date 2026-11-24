struct S_00011B90
{
    int a, b, c, d;
    S_00011B90* FUN_00011b90();
};

// The unit holds 5 trailing bytes (8B C1 C2 04 00) at 0x00011BA0 after the function; their start is missing (F-0130).
// 0x00011B90
// parked: unclassified
S_00011B90* S_00011B90::FUN_00011b90()
{
    a = 0;
    b = 0;
    c = 0;
    d = 0;
    return this;
}
