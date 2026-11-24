struct E80 { char d[80]; };
struct S_0005AA30 {
    char pad[0x5018];
    E80 e[1];
    E80* FUN_0005aa30(int i);
};
// 0x0005AA30
E80* S_0005AA30::FUN_0005aa30(int i)
{
    return &e[i];
}
