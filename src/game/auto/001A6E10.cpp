struct S_001A6E10
{
    int a;
    int b;
    S_001A6E10* FUN_001a6e10();
};

// The unit holds a second function after this one that Ghidra does not know (F-0078).
// 0x001A6E10
// parked: unclassified
S_001A6E10* S_001A6E10::FUN_001a6e10()
{
    a = 0;
    b = 0;
    return this;
}
