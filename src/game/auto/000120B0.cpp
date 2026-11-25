struct S_000120B0
{
    int a;
    int b;
    int c;
    int d;
    S_000120B0* FUN_000120b0();
};

// The unit holds a second function after this one that Ghidra does not know (F-0078).
// 0x000120B0
// parked: unclassified
S_000120B0* S_000120B0::FUN_000120b0()
{
    a = 0;
    b = 0;
    c = 0;
    d = 0;
    return this;
}
