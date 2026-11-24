struct S_001A32B0 {
    char pad[0x16a];
    short f;
    void FUN_001a32b0(bool b);
};

// 0x001A32B0
void S_001A32B0::FUN_001a32b0(bool b)
{
    f = !b;
}
