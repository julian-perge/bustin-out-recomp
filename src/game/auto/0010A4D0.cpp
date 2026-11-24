struct S_0010A4D0
{
    unsigned v;
    void FUN_0010A4D0(const unsigned& x);
};

// 0x0010A4D0
// parked: source shape
void S_0010A4D0::FUN_0010A4D0(const unsigned& x)
{
    v = (v & 0xFFFF8000) | x;
}
