struct S_000DC060
{
    char pad[0x38];
    unsigned char f;
    void FUN_000dc060(bool b);
};

// 0x000DC060
void S_000DC060::FUN_000dc060(bool b)
{
    if (b)
        f |= 0x80;
    else
        f &= ~0x80;
}
