extern "C" void* memset(void*, int, unsigned);

struct S_001430C0
{
    int d[21];
    S_001430C0();
};

// 0x001430C0
S_001430C0::S_001430C0()
{
    memset(this, 0, sizeof(*this));
}
