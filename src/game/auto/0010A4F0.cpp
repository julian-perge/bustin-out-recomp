struct S_0010A4F0
{
    unsigned int flags;
    void FUN_0010a4f0(int on);
};

// 0x0010A4F0
// parked: source shape
void S_0010A4F0::FUN_0010a4f0(int on)
{
    flags &= ~0x8000u;
    if (on) {
        flags |= 0x8000;
    }
}
