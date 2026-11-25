struct S_0019F090
{
    char pad[0x160];
    short v;
    virtual void s0();
    virtual void s1();
    virtual int s2();
    void FUN_0019f090(int n);
};

// 0x0019F090
void S_0019F090::FUN_0019f090(int n)
{
    if (n > s2()) {
        v = (short)n;
    }
}
