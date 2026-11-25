struct S_001A6C80
{
    int x;
    int y;
    int FUN_001a6c80(const S_001A6C80* o);
};

// 0x001A6C80
int S_001A6C80::FUN_001a6c80(const S_001A6C80* o)
{
    int dy = o->y - y;
    int dx = o->x - x;
    return dx * dx + dy * dy;
}
