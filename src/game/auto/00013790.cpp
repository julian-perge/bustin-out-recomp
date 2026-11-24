struct S_00013790
{
    float x, y, z;
    S_00013790* FUN_00013790(const S_00013790* o);
};

// 0x00013790
S_00013790* S_00013790::FUN_00013790(const S_00013790* o)
{
    x = o->x;
    y = o->y;
    z = o->z;
    return this;
}
