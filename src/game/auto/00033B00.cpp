struct N_00033B00
{
    N_00033B00* next;
};

struct S_00033B00
{
    N_00033B00* t[64];
    void FUN_00033b00(N_00033B00* n, unsigned i);
};

// 0x00033B00
void S_00033B00::FUN_00033b00(N_00033B00* n, unsigned i)
{
    unsigned h = i & 0x3f;
    n->next = t[h];
    t[h] = n;
}
