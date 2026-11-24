struct S_00208300
{
    struct E
    {
        char pad[20];
    };
    E* begin;
    E* end;
    int FUN_00208300();
};

// 0x00208300
int S_00208300::FUN_00208300()
{
    return end - begin;
}
