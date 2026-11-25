struct Src_0016F590
{
    char pad0;
    unsigned char small;
    char pad2[2];
    int word;
};

struct S_0016F590
{
    char pad[0x3B274];
    int word;
    unsigned small;
    void FUN_0016F590(const Src_0016F590* s);
};

// 0x0016F590
void S_0016F590::FUN_0016F590(const Src_0016F590* s)
{
    word = s->word;
    small = s->small;
}
