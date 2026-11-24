struct S_000EAA70_Inner
{
    virtual void FUN_s00();
    virtual void FUN_s01();
    virtual void FUN_s02(int a);
};

struct S_000EAA70_Owner
{
    char pad[0x84];
    S_000EAA70_Inner* t;
};

struct S_000EAA70
{
    char pad[8];
    S_000EAA70_Owner* o;
    char pad2[0xc];
    int state;
    void FUN_000eaa70(int a);
};

// 0x000EAA70
void S_000EAA70::FUN_000eaa70(int a)
{
    if (state == 1)
        o->t->FUN_s02(a);
}
