struct S_00208540
{
    struct E
    {
        char pad[88];
    };
    E* begin;
    E* mid;
    E* end;
    int FUN_00208540();
};

// 0x00208540
int S_00208540::FUN_00208540()
{
    return end - begin;
}
