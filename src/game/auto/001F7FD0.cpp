struct S_001F7FD0_E { int a[5]; };
struct S_001F7FD0_I {
    int a;
    S_001F7FD0_E* arr;
};
struct S_001F7FD0 {
    int a;
    int b;
    S_001F7FD0_I* p;
    S_001F7FD0_E* FUN_001f7fd0(int i);
};

// 0x001F7FD0
S_001F7FD0_E* S_001F7FD0::FUN_001f7fd0(int i)
{
    return p->arr + i;
}
