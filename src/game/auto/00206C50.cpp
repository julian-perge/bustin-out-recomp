struct S_00206C50
{
    S_00206C50* FUN_00206c50(int a);
};

// 0x00206C50
S_00206C50* S_00206C50::FUN_00206c50(int a)
{
    if (a == 0x11)
        return this;
    return a == 0x10 ? this : 0;
}
