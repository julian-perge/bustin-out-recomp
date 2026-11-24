extern "C" void* memset(void*, int, unsigned);

struct S_000335A0
{
    int a;
    int b[16];
    S_000335A0();
};

// 0x000335A0
S_000335A0::S_000335A0()
{
    a = 0;
    memset(b, 0, sizeof(b));
}
