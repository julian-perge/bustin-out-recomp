struct S_001F5440
{
    char pad[0x10];
    unsigned v;
    bool FUN_001f5440();
};

// 0x001F5440
bool S_001F5440::FUN_001f5440()
{
    return v != 0 && v < 0x111;
}
