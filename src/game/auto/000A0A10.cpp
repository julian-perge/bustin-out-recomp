struct S_000A0A10
{
    char pad[0xF76];
    char c;
    char pad2[0xFD0 - 0xF77];
    int p;
    void fn_000A0A10();
};
// 0x000A0A10
void S_000A0A10::fn_000A0A10()
{
    c = (p != 0) + 1;
}
