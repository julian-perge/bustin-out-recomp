struct S_0010EF30
{
    unsigned int lo : 16;
    unsigned int hi : 16;
    void FUN_0010ef30();
};

// 0x0010EF30
// parked: source shape
void S_0010EF30::FUN_0010ef30()
{
    unsigned int t = hi - 1;
    hi = 0;
    *(unsigned int *)this |= t << 16;
}
