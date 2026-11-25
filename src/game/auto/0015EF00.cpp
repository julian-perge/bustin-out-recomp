struct Slot_0015EF00
{
    char pad[0x34];
    unsigned char value;
    char rest[0x40 - 0x35];
};

struct S_0015EF00
{
    Slot_0015EF00 slots[4];
    unsigned char FUN_0015EF00(unsigned char i);
};

// 0x0015EF00
unsigned char S_0015EF00::FUN_0015EF00(unsigned char i)
{
    if (i >= 4)
        return 0;
    return slots[i].value;
}
