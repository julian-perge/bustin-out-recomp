struct E_001C9BE0
{
    char pad[100];
};

struct S_001C9BE0
{
    E_001C9BE0* b;
    E_001C9BE0* e;
    int FUN_001c9be0();
};

// 0x001C9BE0
int S_001C9BE0::FUN_001c9be0()
{
    return e - b;
}
