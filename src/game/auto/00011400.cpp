struct Src_00011400
{
    virtual void v0();
    virtual void v1();
    virtual void v2();
    virtual void v3();
    virtual float v4(void* arg);
};

extern Src_00011400* DAT_0035d1a0;
extern int DAT_0035d220;

struct S_00011400
{
    float pad;
    float base;
    float fn_00011400();
};

// 0x00011400
float S_00011400::fn_00011400()
{
    return DAT_0035d1a0->v4(&DAT_0035d220) - base;
}
