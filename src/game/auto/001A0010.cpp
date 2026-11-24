// 0x001A0010
void FUN_001a0010(int* a, int* b)
{
    int t = *a;
    *a = *b;
    *b = t;
}
