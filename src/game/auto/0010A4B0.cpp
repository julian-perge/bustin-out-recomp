struct S_0010a4b0
{
    unsigned v;
    void SetHi(unsigned short h) { ((unsigned short*)this)[1] = h; }
    void FUN_0010a4b0(unsigned x);
};

// 0x0010A4B0
// parked: source shape
void S_0010a4b0::FUN_0010a4b0(unsigned x)
{
    SetHi(0);
    v = v | (x << 16);
}
