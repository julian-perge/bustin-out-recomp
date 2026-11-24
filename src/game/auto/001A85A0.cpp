struct Info_001A85A0
{
    char pad[0x7a];
    short s;
};

struct Res_001A85A0
{
    char pad[0x18];
    Info_001A85A0* info;
};

struct Owner_001A85A0;

struct Mgr_001A85A0
{
    virtual void v0();
    virtual void v1();
    virtual void v2();
    virtual void v3();
    virtual void v4();
    virtual void v5();
    virtual void v6();
    virtual void v7();
    virtual void v8();
    virtual void v9();
    virtual void v10();
    virtual void v11();
    virtual void v12();
    virtual void v13();
    virtual void v14();
    virtual void v15();
    virtual void v16();
    virtual void v17();
    virtual Res_001A85A0* get(Owner_001A85A0* o);
};

struct Owner_001A85A0
{
    char pad[0x30];
    Mgr_001A85A0* mgr;
};

struct S_001A85A0
{
    int FUN_001a85a0();
};

struct Base_001A85A0
{
    Owner_001A85A0* owner;
    char pad[0x64];
};

// 0x001A85A0
int S_001A85A0::FUN_001a85a0()
{
    Owner_001A85A0* o = ((Base_001A85A0*)((char*)this - 0x68))->owner;
    Res_001A85A0* r = o->mgr->get(o);
    if (!r)
        return 0;
    return r->info->s;
}
