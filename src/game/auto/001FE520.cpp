struct S_001FE520
{
    int a;
    int b;
    S_001FE520* FUN_001fe520(const S_001FE520* o);
};

// 0x001FE520
S_001FE520* S_001FE520::FUN_001fe520(const S_001FE520* o)
{
    a = o->a;
    b = o->b;
    return this;
}
