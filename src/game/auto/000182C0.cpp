struct S_000182C0
{
    float x;
    float y;
    float z;
    float FUN_000182c0(const S_000182C0* o);
};

// 0x000182C0
float S_000182C0::FUN_000182c0(const S_000182C0* o)
{
    return x * o->x + y * o->y + z * o->z;
}
