struct S_001C4290
{
    short pad;
    short a;
    short b;
    void FUN_001c4290(short v);
};

// The unit holds 5 trailing bytes (0F BF 41 10 C3) at 0x001C42A0 after the function; their start is missing (F-0138).
// 0x001C4290
// parked: unclassified
void S_001C4290::FUN_001c4290(short v)
{
    b = v - a;
}
