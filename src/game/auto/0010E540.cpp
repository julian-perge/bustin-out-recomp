extern "C" void* __cdecl memset(void*, int, unsigned int);

struct S_0010E540
{
    int n;
    int a[256];
    void FUN_0010e540();
};

// 0x0010E540
void S_0010E540::FUN_0010e540()
{
    n = 0;
    memset(a, 0, sizeof(a));
}
