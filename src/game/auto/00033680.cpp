extern "C" void* memset(void*, int, unsigned);

struct S_00033680
{
    int a;
    int b[16];
    S_00033680();
};

// 0x00033680
S_00033680::S_00033680()
{
    a = 0;
    memset(b, 0, sizeof(b));
}
