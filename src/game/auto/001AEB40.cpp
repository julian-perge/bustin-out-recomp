// F-0120: the only references are SUB ECX,[ECX-4]; JMP thunks, and the function reads members at negative offsets from this.
struct S_001AEB40
{
    void FUN_001aeb40(int* p);
};

// The cast stands in for the class layout of a virtual base, which VC71 generates (F-0120).
// 0x001AEB40
// parked: source shape
void S_001AEB40::FUN_001aeb40(int* p)
{
    const int* s = (const int*)((const char*)this - 0x8c);
    p[0] = s[0];
    p[1] = s[1];
}
