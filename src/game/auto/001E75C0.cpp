extern "C" void* __cdecl memset(void*, int, unsigned int);
struct S_001E75C0
{
    char pad[0x2944];
    int v[0x50];
    void FUN_001e75c0();
};

// 0x001E75C0
void S_001E75C0::FUN_001e75c0()
{
    memset(v, 0, sizeof(v));
}
