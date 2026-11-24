struct S_00051E80 {
    char pad[0x24];
    char v;
};
// 0x00051E80
int FUN_00051e80(S_00051E80* a, char* b)
{
    *b = a->v;
    a->v = 0;
    return 0;
}
