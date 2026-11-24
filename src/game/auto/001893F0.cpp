extern "C" void* memset(void*, int, unsigned);

struct S_001893F0
{
    int d[15];
    S_001893F0();
};

// 0x001893F0
S_001893F0::S_001893F0()
{
    memset(this, 0, sizeof(*this));
}
