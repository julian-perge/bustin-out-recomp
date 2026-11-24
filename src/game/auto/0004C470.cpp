struct S_0004C470 {
    char pad[0x3c];
    float lo, hi;
    bool FUN_0004c470();
};
// 0x0004C470
bool S_0004C470::FUN_0004c470()
{
    return hi >= lo;
}
