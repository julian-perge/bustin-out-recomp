struct S_001F3770_node
{
    S_001F3770_node* next;
};

struct S_001F3770
{
    S_001F3770_node* head;
    int FUN_001f3770();
};

// 0x001F3770
int S_001F3770::FUN_001f3770()
{
    int n = 0;
    S_001F3770_node* end = head;
    for (S_001F3770_node* p = end->next; p != end; p = p->next) {
        n++;
    }
    return n;
}
