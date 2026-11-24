struct S_000335C0
{
    int n;
    int items[1];
    void FUN_000335c0(int v);
};

// The unit holds 7 trailing bytes (83 39 00 0F 95 C0 C3) at 0x000335D0 after the function; their start is missing (F-0145).
// 0x000335C0
// parked: unclassified
void S_000335C0::FUN_000335c0(int v)
{
    items[n] = v;
    n++;
}
