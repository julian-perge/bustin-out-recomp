struct S_002082A0
{
    struct E
    {
        char pad[88];
    };
    E* begin;
    E* end;
    int FUN_002082a0();
};

// 0x002082A0
int S_002082A0::FUN_002082a0()
{
    return end - begin;
}
