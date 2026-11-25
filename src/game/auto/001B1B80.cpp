struct Node_001B1B80
{
    char c;
    int a;
    Node_001B1B80* b;
    Node_001B1B80* d;
};

struct S_001B1B80
{
    Node_001B1B80* n;
    void FUN_001b1b80();
};

// 0x001B1B80
void S_001B1B80::FUN_001b1b80()
{
    n->c = 0;
    n->a = 0;
    n->b = n;
    n->d = n;
}
