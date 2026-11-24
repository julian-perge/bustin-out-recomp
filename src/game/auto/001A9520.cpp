struct S_001A9520Outer
{
    int a;
    int b;
    char pad[0x2c];
    int tail;
};

struct S_001A9520
{
    void FUN_001a9520(int *pa, int *pb);
};

// The function is reached only through virtual-base thunks, so the cast stands in for a class layout that VC71 generates (F-0120).
// 0x001A9520
// parked: source shape
void S_001A9520::FUN_001a9520(int *pa, int *pb)
{
    S_001A9520Outer *o = (S_001A9520Outer *)((char *)this - 0x34);
    *pa = o->a;
    *pb = o->b;
}
