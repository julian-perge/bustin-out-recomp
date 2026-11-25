extern "C" void* memset(void*, int, unsigned);

struct S_00033CF0
{
    int a;
    int b[16];
    int c;
    void FUN_00033CF0();
};

// 0x00033CF0
void S_00033CF0::FUN_00033CF0()
{
    a = 0;
    memset(b, 0, sizeof(b));
    c = 0;
}
