struct S_0007B310_E
{
    char pad[112];
};

struct S_0007B310
{
    S_0007B310_E* p;
    S_0007B310_E* FUN_0007b310(int n);
};

// 0x0007B310
S_0007B310_E* S_0007B310::FUN_0007b310(int n)
{
    return p + n;
}
