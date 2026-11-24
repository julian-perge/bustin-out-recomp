struct S_000E4E40
{
    char pad[0x98];
    short s;
    void fn_000E4E40(bool b);
};
// 0x000E4E40
void S_000E4E40::fn_000E4E40(bool b)
{
    s = (b != false);
}
