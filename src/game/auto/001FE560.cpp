struct S_001FE560
{
    int a;
    int b;
    S_001FE560* FUN_001fe560(const S_001FE560* o);
};

// 0x001FE560
S_001FE560* S_001FE560::FUN_001fe560(const S_001FE560* o)
{
    a = o->a;
    b = o->b;
    return this;
}
