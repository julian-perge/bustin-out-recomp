struct S_000DEB00
{
    char pad[0xb];
    unsigned char f;
    void FUN_000deb00(bool b);
};

// 0x000DEB00
void S_000DEB00::FUN_000deb00(bool b)
{
    if (b)
        f |= 0x10;
    else
        f &= ~0x10;
}
