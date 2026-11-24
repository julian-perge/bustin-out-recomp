struct S_001FF940
{
    int a;
    int b;
    S_001FF940* FUN_001ff940(const S_001FF940* o);
};

// 0x001FF940
S_001FF940* S_001FF940::FUN_001ff940(const S_001FF940* o)
{
    a = o->a;
    b = o->b;
    return this;
}
