struct P_001DB720
{
    int x;
    int y;
};

// 0x001DB720
void FUN_001db720(P_001DB720* dst, const P_001DB720* src)
{
    if (dst)
    {
        dst->x = src->x;
        dst->y = src->y;
    }
}
