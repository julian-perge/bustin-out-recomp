struct S_0010B770 {
    unsigned int v;
    char pad[0x48];
    int m;
    int FUN_0010b770();
};
// 0x0010B770
// parked: unclassified
int S_0010B770::FUN_0010b770()
{
    return !((v & 0x7fff) - 3);
}
