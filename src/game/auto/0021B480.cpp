struct S_0021B480
{
    unsigned char v;
    bool FUN_0021b480(const S_0021B480* o);
};

// 0x0021B480
bool S_0021B480::FUN_0021b480(const S_0021B480* o)
{
    return (v & 0xf0) < (o->v & 0xf0);
}
