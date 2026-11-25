struct S_00200DE0
{
    S_00200DE0* FUN_00200de0(int a);
};

// 0x00200DE0
S_00200DE0* S_00200DE0::FUN_00200de0(int a)
{
    if (a == 0x13)
        return this;
    return a == 0x12 ? this : 0;
}
