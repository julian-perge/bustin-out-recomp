struct S_001FB650
{
    void FUN_001fb650(int v);
};

// The function is reached through a virtual-base layout (vbptr at +4, two vbase hops), so the cast stands in for a class layout that VC71 generates (F-0120).
// 0x001FB650
// parked: source shape
void S_001FB650::FUN_001fb650(int v)
{
    char* b = (char*)this + 4 + ((int*)*(int*)((char*)this + 4))[2];
    char* c = *(char**)(b + 0x20);
    *(int*)(b + *(int*)(c + 4) + 0x2c) = v;
}
