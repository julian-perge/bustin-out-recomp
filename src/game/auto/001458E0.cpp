struct Vec2_001458E0
{
    float x;
    float y;
};

struct Vec3_001458E0
{
    float x;
    float y;
    float z;
    void setXZ(const Vec2_001458E0* v)
    {
        x = v->x;
        z = v->y;
    }
};

struct S_001458E0
{
    virtual void s0();
    virtual void s1();
    virtual void s2();
    virtual void s3();
    virtual void s4();
    virtual void s5();
    virtual void s6();
    virtual void s7();
    virtual void s8();
    virtual void s9();
    virtual void s10();
    virtual void s11();
    virtual void s12();
    virtual void s13();
    virtual void s14();
    virtual void s15();
    virtual void s16();
    virtual void s17();
    virtual void s18();
    virtual void s19();
    virtual void s20();
    char pad[0x24 - 4];
    Vec3_001458E0 pos;
    void FUN_001458e0(const Vec2_001458E0* v);
};

// 0x001458E0
void S_001458E0::FUN_001458e0(const Vec2_001458E0* v)
{
    pos.setXZ(v);
    s20();
}
