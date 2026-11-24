struct S_001DAD40_target
{
    virtual void s0();
    virtual void s1();
    virtual void s2();
    virtual void s3();
    virtual void s4();
    virtual void s5();
    virtual void s6();
    virtual void FUN_001DAD40_slot();
};

struct S_001DAD40
{
    void FUN_001DAD40();
};

// 0x001DAD40
// parked: source shape
void S_001DAD40::FUN_001DAD40()
{
    char* b = (char*)this;
    (*(S_001DAD40_target**)(b - 0x160))->FUN_001DAD40_slot();
    *(short*)(b - 0x540) = 0;
}
