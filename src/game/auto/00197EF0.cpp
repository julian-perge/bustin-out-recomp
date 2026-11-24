struct S_00197EF0
{
    char a;
    char b;
    S_00197EF0& fn_00197EF0(const S_00197EF0& o);
};
// 0x00197EF0
S_00197EF0& S_00197EF0::fn_00197EF0(const S_00197EF0& o)
{
    a += o.a;
    b += o.b;
    return *this;
}
