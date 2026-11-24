struct S_001B0080
{
    unsigned v;
    bool FUN_001b0080(unsigned m);
};

// 0x001B0080
bool S_001B0080::FUN_001b0080(unsigned m)
{
    return (v & m) == m;
}
