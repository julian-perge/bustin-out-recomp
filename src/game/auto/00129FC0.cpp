struct S_00129FC0
{
    char pad[0x54];
    bool b[8];
    void fn_00129FC0(int i);
};
// 0x00129FC0
void S_00129FC0::fn_00129FC0(int i)
{
    b[i] = !b[i];
}
