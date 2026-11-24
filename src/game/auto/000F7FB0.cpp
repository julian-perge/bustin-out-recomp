struct E_000F7FB0
{
    char pad[76];
};

struct S_000F7FB0
{
    E_000F7FB0* first;
    E_000F7FB0* last;
    int FUN_000f7fb0();
};

// 0x000F7FB0
int S_000F7FB0::FUN_000f7fb0()
{
    return last - first;
}
