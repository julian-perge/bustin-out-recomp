extern "C" void* memset(void*, int, unsigned);

struct S_0010E980
{
    int a;
    int b[128];
    S_0010E980();
};

// 0x0010E980
S_0010E980::S_0010E980()
{
    a = 0;
    memset(b, 0, sizeof(b));
}
