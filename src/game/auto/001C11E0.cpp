struct E_001C11E0
{
    char pad[16];
};

struct S_001C11E0
{
    E_001C11E0* p;
    E_001C11E0* FUN_001c11e0();
};

// 0x001C11E0
E_001C11E0* S_001C11E0::FUN_001c11e0()
{
    return p + (p ? ((int*)p)[-1] : 0);
}
