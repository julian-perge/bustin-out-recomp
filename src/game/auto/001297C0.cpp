struct S_001297C0Blk
{
    int d[17];
};

struct S_001297C0
{
    char pad[0x48];
    S_001297C0Blk blk;
    void FUN_001297c0(const S_001297C0Blk *src);
};

// 0x001297C0
void S_001297C0::FUN_001297c0(const S_001297C0Blk *src)
{
    blk = *src;
}
