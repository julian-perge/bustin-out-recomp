struct S_001AEF90_Target
{
    virtual void FUN_s00();
    virtual void FUN_s01();
    virtual void FUN_s02();
    virtual void FUN_s03();
    virtual void FUN_s04();
    virtual void FUN_s05();
    virtual void FUN_s06();
    virtual void FUN_s07();
    virtual void FUN_s08();
    virtual void FUN_s09();
    virtual void FUN_s10();
    virtual void FUN_s11();
    virtual void FUN_s12();
    virtual void FUN_s13();
    virtual void FUN_s14();
    virtual void FUN_s15();
    virtual void FUN_s16();
    virtual void FUN_s17();
    virtual int FUN_s18(int x);
};

struct S_001AEF90
{
    int FUN_001aef90(short x);
};

// 0x001AEF90
int S_001AEF90::FUN_001aef90(short x)
{
    return (*(S_001AEF90_Target**)((char*)this - 0x9c))->FUN_s18(x);
}
