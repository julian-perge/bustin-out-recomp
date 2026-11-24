struct S_000FEAF0
{
    char pad[0x351];
    char c;
    char fn_000FEAF0(char v);
};
// 0x000FEAF0
char S_000FEAF0::fn_000FEAF0(char v)
{
    char o = c;
    c = v;
    return o;
}
