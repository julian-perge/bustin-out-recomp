struct S_001F38B0_node
{
    S_001F38B0_node* next;
};

struct S_001F38B0
{
    int a;
    int b;
    S_001F38B0_node* head;
    int FUN_001f38b0();
};

// 0x001F38B0
int S_001F38B0::FUN_001f38b0()
{
    int n = 0;
    S_001F38B0_node* end = head;
    for (S_001F38B0_node* p = end->next; p != end; p = p->next) {
        n++;
    }
    return n;
}
