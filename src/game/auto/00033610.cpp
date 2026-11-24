extern "C" void* __cdecl memset(void*, int, unsigned int);

struct S_00033610
{
    int n;
    int items[16];
    void FUN_00033610();
};

// 0x00033610
void S_00033610::FUN_00033610()
{
    n = 0;
    memset(items, 0, sizeof(items));
}
