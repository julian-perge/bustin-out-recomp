// 0x000B1770
void fn_000B1770(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

struct Link_000BB2E0
{
    Link_000BB2E0* next;
};

struct S_000BB2E0
{
    Link_000BB2E0* head;
    void fn_000BB2E0(Link_000BB2E0* n);
};

// 0x000BB2E0
void S_000BB2E0::fn_000BB2E0(Link_000BB2E0* n)
{
    if (n) {
        n->next = head;
        head = n;
    }
}

// 0x000BB340
void fn_000BB340(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

struct S_000BE9E0
{
    int a;
    int b;
    S_000BE9E0* fn_000BE9E0(int x, int y);
};
// 0x000BE9E0
S_000BE9E0* S_000BE9E0::fn_000BE9E0(int x, int y)
{
    a = x;
    b = y;
    return this;
}
