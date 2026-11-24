struct S_001C28E0
{
    unsigned short v;
    bool FUN_001c28e0();
};

// 0x001C28E0
bool S_001C28E0::FUN_001c28e0()
{
    return v != 0xffff && (v & 0x8000) != 0;
}
