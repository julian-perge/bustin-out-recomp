struct S_00119fb0
{
    union {
        unsigned v;
        struct {
            unsigned short lo;
            unsigned short hi;
        };
    };
    int w;
    void FUN_00119fb0(int x);
};

// 0x00119FB0
// parked: source shape
void S_00119fb0::FUN_00119fb0(int x)
{
    hi = 0;
    v |= 0x80000000;
    w = x;
}
