// F-0120: the only references are SUB ECX,[ECX-4]; JMP thunks, and the function reads a member at this-0x14c.
struct S_001AE550
{
    short* arr;
    void FUN_001ae550(int i, short v);
};

// 0x001AE550
// parked: source shape
void S_001AE550::FUN_001ae550(int i, short v)
{
    arr[i] = v;
}
