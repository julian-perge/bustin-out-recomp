struct S_0008AE50
{
    char pad[0x328];
    unsigned int flags;
    void FUN_0008ae50(bool on);
};

// 0x0008AE50
void S_0008AE50::FUN_0008ae50(bool on)
{
    if (on) {
        flags |= 4;
    } else {
        flags &= ~4u;
    }
}
