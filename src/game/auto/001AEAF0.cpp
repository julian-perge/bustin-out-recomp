// F-0120: the only references are SUB ECX,[ECX-4]; JMP thunks, and the function reads members at negative offsets from this.
struct S_001AEAF0
{
    void FUN_001aeaf0(const int* p);
};

// The cast stands in for the class layout of a virtual base, which VC71 generates (F-0120).
// 0x001AEAF0
// parked: source shape
void S_001AEAF0::FUN_001aeaf0(const int* p)
{
    int* d = (int*)((char*)this - 0x8c);
    d[0] = p[0];
    d[1] = p[1];
}
