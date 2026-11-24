struct S_001FF920
{
    int a;
    int b;
    S_001FF920* FUN_001ff920(const S_001FF920* o);
};

// 0x001FF920
S_001FF920* S_001FF920::FUN_001ff920(const S_001FF920* o)
{
    a = o->a;
    b = o->b;
    return this;
}
