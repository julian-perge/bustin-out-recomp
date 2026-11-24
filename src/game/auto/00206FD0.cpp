struct S_00206FD0_elem
{
    int v[3];
};

struct S_00206FD0
{
    S_00206FD0_elem* p;
    S_00206FD0_elem* FUN_00206FD0();
};

// 0x00206FD0
S_00206FD0_elem* S_00206FD0::FUN_00206FD0()
{
    int n = p ? ((int*)p)[-1] : 0;
    return p + n;
}
