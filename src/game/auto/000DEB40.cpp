struct S_000DEB40
{
    char pad[0xb];
    unsigned char f;
    void FUN_000deb40(bool b);
};

// 0x000DEB40
void S_000DEB40::FUN_000deb40(bool b)
{
    if (b)
        f |= 0x40;
    else
        f &= ~0x40;
}
