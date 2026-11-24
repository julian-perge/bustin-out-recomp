struct S_001B5570 {
    int x;
    int y;
    S_001B5570& FUN_001b5570(const S_001B5570& o);
};

// 0x001B5570
S_001B5570& S_001B5570::FUN_001b5570(const S_001B5570& o)
{
    y -= o.y;
    x -= o.x;
    return *this;
}
