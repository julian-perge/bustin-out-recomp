struct S_000C7E90_Elem
{
    char pad[32];
};

struct S_000C7E90
{
    S_000C7E90_Elem* p;
    S_000C7E90_Elem* FUN_000c7e90();
};

// 0x000C7E90
S_000C7E90_Elem* S_000C7E90::FUN_000c7e90()
{
    return p + (p ? ((int*)p)[-1] : 0);
}
