struct S_001C0A20_Inner {
    int a;
    int b;
    short s;
};
struct S_001C0A20 {
    int a;
    int b;
    S_001C0A20_Inner* p;
    short FUN_001c0a20();
};

// The unit holds 3 trailing bytes (33 C0 C3, LAB_001c0a30) after the function; their start is missing (F-0124).
// 0x001C0A20
short S_001C0A20::FUN_001c0a20()
{
    if (p)
        return p->s;
    return 0;
}
