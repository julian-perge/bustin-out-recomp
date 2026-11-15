struct Host_000C1900
{
    virtual void v0();
    virtual void v1();
    virtual void v2();
    virtual void v3();
    virtual void v4();
    virtual void v5();
    virtual void v6();
    virtual void v7(void (*callback)());
};

extern Host_000C1900* DAT_0035ddf8;
extern bool DAT_00321a3c;

void FUN_000c18e0();
void FUN_000c1920();
void FUN_000c1a40();
void FUN_000c1aa0();
void FUN_000c1b30();

// 0x000C1900
void fn_000C1900()
{
    DAT_00321a3c = false;
    DAT_0035ddf8->v7(FUN_000c18e0);
}

// 0x000C1A20
void fn_000C1A20()
{
    DAT_00321a3c = false;
    DAT_0035ddf8->v7(FUN_000c1920);
}

// 0x000C1A80
void fn_000C1A80()
{
    DAT_00321a3c = false;
    DAT_0035ddf8->v7(FUN_000c1a40);
}

// 0x000C1B10
void fn_000C1B10()
{
    DAT_00321a3c = false;
    DAT_0035ddf8->v7(FUN_000c1aa0);
}

// 0x000C1B50
void fn_000C1B50()
{
    DAT_00321a3c = false;
    DAT_0035ddf8->v7(FUN_000c1b30);
}
