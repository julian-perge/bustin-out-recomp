struct S_002003B0_node
{
    char c;
    int a;
    S_002003B0_node* l;
    S_002003B0_node* r;
};

struct S_002003B0
{
    S_002003B0_node* head;
    void FUN_002003B0();
};

// 0x002003B0
void S_002003B0::FUN_002003B0()
{
    head->c = 0;
    head->a = 0;
    head->l = head;
    head->r = head;
}
