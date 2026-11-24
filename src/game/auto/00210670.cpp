struct S_00210670
{
    struct E
    {
        char pad[44];
    };
    E* begin;
    E* end;
    int FUN_00210670();
};

// 0x00210670
int S_00210670::FUN_00210670()
{
    return end - begin;
}
