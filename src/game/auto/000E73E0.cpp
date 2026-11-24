struct S_000e73e0
{
    float a;
    float b;
    float c;
    char mode;
    float FUN_000e73e0();
};

// 0x000E73E0
float S_000e73e0::FUN_000e73e0()
{
    if (!mode)
        return (a - c) * b;
    return c * b;
}
