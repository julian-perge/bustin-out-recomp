struct S_00197F10
{
    char a;
    char b;
    S_00197F10& fn_00197F10(const S_00197F10& o);
};
// 0x00197F10
S_00197F10& S_00197F10::fn_00197F10(const S_00197F10& o)
{
    a -= o.a;
    b -= o.b;
    return *this;
}
