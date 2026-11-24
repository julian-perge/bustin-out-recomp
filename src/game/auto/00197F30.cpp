struct S_00197F30
{
    unsigned char a;
    unsigned char b;
    S_00197F30* FUN_00197f30(char m);
};

// 0x00197F30
S_00197F30* S_00197F30::FUN_00197f30(char m)
{
    a = a * m;
    b = b * m;
    return this;
}
