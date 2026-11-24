extern "C" void* __cdecl memset(void*, int, unsigned int);

struct S_0010E560
{
    int n;
    int a[128];
    void FUN_0010e560();
};

// 0x0010E560
void S_0010E560::FUN_0010e560()
{
    n = 0;
    memset(a, 0, sizeof(a));
}
