struct S_002003D0_node
{
    char c;
    int a;
    S_002003D0_node* l;
    S_002003D0_node* r;
};

struct S_002003D0
{
    S_002003D0_node* head;
    void FUN_002003D0();
};

// 0x002003D0
void S_002003D0::FUN_002003D0()
{
    head->c = 0;
    head->a = 0;
    head->l = head;
    head->r = head;
}
