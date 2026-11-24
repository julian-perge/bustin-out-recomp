struct S_00208790
{
    struct E
    {
        char pad[20];
    };
    E* begin;
    E* end;
    int FUN_00208790();
};

// 0x00208790
int S_00208790::FUN_00208790()
{
    return end - begin;
}
