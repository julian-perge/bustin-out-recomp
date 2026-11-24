struct S_00035A70_B
{
    unsigned a : 3;
    unsigned b : 1;
    void set() { a = 0; b = 1; }
};

struct S_00035A70
{
    S_00035A70_B x;
    S_00035A70_B y;
    void FUN_00035a70();
};

// 0x00035A70
void S_00035A70::FUN_00035a70()
{
    y.set();
    x.set();
}
