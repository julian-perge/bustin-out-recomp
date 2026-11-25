struct N_001F5C10
{
    char pad[0x14];
    N_001F5C10* next;
};

struct S_001F5C10
{
    N_001F5C10* heads[256];
    void FUN_001f5c10(N_001F5C10* n, int i);
};

// 0x001F5C10
void S_001F5C10::FUN_001f5c10(N_001F5C10* n, int i)
{
    int k = i & 0xff;
    N_001F5C10* h = heads[k];
    n->next = h;
    heads[k] = n;
}
