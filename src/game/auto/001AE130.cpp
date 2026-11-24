// F-0078: the unit holds an 8-byte thunk (SUB ECX,[ECX-4]; JMP 0x001A8FD0) after the function, and Ghidra has no function start there.
// F-0120: the only references are SUB ECX,[ECX-4]; JMP thunks, and the function reads members at negative offsets from this.
struct S_001AE130
{
    bool FUN_001ae130(unsigned m);
};

// The cast stands in for the class layout of a virtual base, which VC71 generates (F-0120).
// 0x001AE130
// parked: source shape
bool S_001AE130::FUN_001ae130(unsigned m)
{
    return (*(const unsigned*)((const char*)this - 0x70) & m) != 0;
}
