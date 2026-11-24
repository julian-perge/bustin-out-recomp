struct N_001F54C0
{
    char pad[0x30];
    int next;
};

struct S_001F54C0
{
    char pad[0x404];
    int head;
    void FUN_001f54c0(N_001F54C0* p);
};

// 0x001F54C0
void S_001F54C0::FUN_001f54c0(N_001F54C0* p)
{
    p->next = head;
    head = (int)p;
}
