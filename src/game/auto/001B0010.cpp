extern "C" void* memset(void*, int, unsigned);

struct S_001B0010
{
    int d[11];
    S_001B0010();
};

// 0x001B0010
S_001B0010::S_001B0010()
{
    memset(this, 0, sizeof(*this));
}
