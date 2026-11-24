struct S_000BA9C0
{
    char pad[0x175];
    char c;
    char fn_000BA9C0(char v);
};
// 0x000BA9C0
char S_000BA9C0::fn_000BA9C0(char v)
{
    char o = c;
    c = v;
    return o;
}
