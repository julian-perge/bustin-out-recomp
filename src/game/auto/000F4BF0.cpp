struct S_000F4BF0
{
    int pad0;
    int a;
    int pad8[2];
    float f;
    void FUN_000f4bf0(int x, float y);
};

// 0x000F4BF0
void S_000F4BF0::FUN_000f4bf0(int x, float y)
{
    a = x;
    f = y;
}
