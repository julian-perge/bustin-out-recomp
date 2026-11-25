struct B_000C7BC0
{
    char pad[0xac];
    int n;
    bool Ok(int x) { return x >= n - 2; }
};

struct S_000C7BC0
{
    char pad0[0x3c];
    int i;
    char pad1[0x6c - 0x40];
    B_000C7BC0* p;
    bool FUN_000c7bc0();
};

// The original ends with setge al and no xor ecx; every form tried (bool, unsigned char, helper, local, inverted branch) builds the xor ecx form.
// 0x000C7BC0
// parked: unclassified
bool S_000C7BC0::FUN_000c7bc0()
{
    if (i < 0)
        return false;
    return i >= p->n - 2;
}
