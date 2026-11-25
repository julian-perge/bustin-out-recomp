struct Node_0019B770
{
    char c;
    int a;
    Node_0019B770* b;
    Node_0019B770* d;
};

struct S_0019B770
{
    Node_0019B770* n;
    void FUN_0019b770();
};

// 0x0019B770
void S_0019B770::FUN_0019b770()
{
    n->c = 0;
    n->a = 0;
    n->b = n;
    n->d = n;
}
