
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

struct S_000357A0
{
    int a;
    int b;
    S_000357A0(const S_000357A0& o);
};

// 0x000357A0
S_000357A0::S_000357A0(const S_000357A0& o)
{
    a = o.a;
    b = o.b;
}

struct S_00035A10
{
    unsigned bits;
    void FUN_00035A10(unsigned v);
};

// 0x00035A10
void S_00035A10::FUN_00035A10(unsigned v)
{
    bits = (bits & 0xf) | (v << 4);
}
