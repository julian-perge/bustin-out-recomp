struct S_000F4D80
{
    char pad[0x14];
    float f;
    void fn_000F4D80(float v);
};
// 0x000F4D80
void S_000F4D80::fn_000F4D80(float v)
{
    f += v;
}
