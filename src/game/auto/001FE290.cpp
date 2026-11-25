struct S_001FE290
{
    char pad[0x16];
    unsigned char lo : 8;
    signed char hi : 8;
    void FUN_001fe290(int* a, int* b);
};

// The original loads byte +0x16 into AL and masks with 0xff; every form tried (cast, mask, getter, bitfield) builds movzx.
// 0x001FE290
// parked: unclassified
void S_001FE290::FUN_001fe290(int* a, int* b)
{
    *a = hi;
    *b = lo;
}
