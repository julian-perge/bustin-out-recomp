struct S_0010a4b0
{
    union {
        unsigned v;
        struct {
            unsigned short lo;
            unsigned short hi;
        };
    };
    void FUN_0010a4b0(unsigned x);
};

// 0x0010A4B0
// parked: source shape
void S_0010a4b0::FUN_0010a4b0(unsigned x)
{
    hi = 0;
    v |= x << 16;
}
