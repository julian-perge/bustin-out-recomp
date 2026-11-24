struct S_00156720
{
    char pad[0x30];
    int (*cb)(void* arg, int n);
    int pad2;
    void* arg;
    int FUN_00156720();
};

// 0x00156720
int S_00156720::FUN_00156720()
{
    if (cb)
        return cb(arg, 0);
    return -1;
}
