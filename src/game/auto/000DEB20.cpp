struct S_000DEB20
{
    char pad[0xb];
    unsigned char f;
    void FUN_000deb20(bool b);
};

// 0x000DEB20
void S_000DEB20::FUN_000deb20(bool b)
{
    if (b)
        f |= 0x20;
    else
        f &= ~0x20;
}
