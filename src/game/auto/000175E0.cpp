struct S_000175E0
{
    float x, y, z;
    S_000175E0* FUN_000175e0(const S_000175E0* o);
};

// 0x000175E0
S_000175E0* S_000175E0::FUN_000175e0(const S_000175E0* o)
{
    x = o->x;
    y = o->y;
    z = o->z;
    return this;
}
