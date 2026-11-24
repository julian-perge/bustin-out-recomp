struct S_001F2CE0 {
    int x;
    int y;
    S_001F2CE0& FUN_001f2ce0(const S_001F2CE0& o);
};

// 0x001F2CE0
S_001F2CE0& S_001F2CE0::FUN_001f2ce0(const S_001F2CE0& o)
{
    x = o.x;
    y = o.y;
    return *this;
}
