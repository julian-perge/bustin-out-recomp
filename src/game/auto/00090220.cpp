struct E_00090220
{
    char pad[0x1c];
    unsigned flags;
};

struct S_00090220
{
    char pad[0x148];
    E_00090220* e[8];
    unsigned FUN_00090220(int i);
};

// 0x00090220
unsigned S_00090220::FUN_00090220(int i)
{
    return (e[i]->flags >> 1) & 1;
}
