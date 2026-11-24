// F-0120: the only references are SUB ECX,[ECX-4]; JMP thunks, and the function reads a member at this-0x11e.
// F-0078: the unit holds an 8-byte thunk (SUB ECX,[ECX-4]; JMP 0x001AEE60) after the function, and Ghidra has no function start there.
struct S_001AEE40
{
    unsigned FUN_001aee40();
};

// The cast stands in for the class layout of a virtual base, which VC71 generates (F-0120).
// 0x001AEE40
// parked: source shape
unsigned S_001AEE40::FUN_001aee40()
{
    unsigned short v = *(const unsigned short*)((const char*)this - 0x11e);
    return (v & 0x200) >> 9;
}
