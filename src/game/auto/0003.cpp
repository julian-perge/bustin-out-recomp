
extern "C" void* memset(void*, int, unsigned);

struct S_00033AE0
{
    int a[64];
    S_00033AE0* fn_00033AE0();
};
// 0x00033AE0
S_00033AE0* S_00033AE0::fn_00033AE0()
{
    memset(this, 0, sizeof(*this));
    return this;
}
