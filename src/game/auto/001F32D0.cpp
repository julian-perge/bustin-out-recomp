struct S_001F32D0_node
{
    char c;
    int a;
    S_001F32D0_node* l;
    S_001F32D0_node* r;
};

struct S_001F32D0
{
    S_001F32D0_node* head;
    void FUN_001F32D0();
};

// 0x001F32D0
void S_001F32D0::FUN_001F32D0()
{
    head->c = 0;
    head->a = 0;
    head->l = head;
    head->r = head;
}
