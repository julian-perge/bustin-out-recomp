struct S_00018240
{
    float x;
    float y;
    float z;
    S_00018240* FUN_00018240(const S_00018240* s);
};

// 0x00018240
S_00018240* S_00018240::FUN_00018240(const S_00018240* s)
{
    x = s->x;
    y = s->y;
    z = 0.0f;
    return this;
}
