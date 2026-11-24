extern "C" void* memset(void*, int, unsigned);

struct S_0010E960
{
    int a;
    int b[256];
    S_0010E960();
};

// 0x0010E960
S_0010E960::S_0010E960()
{
    a = 0;
    memset(b, 0, sizeof(b));
}
