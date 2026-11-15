#include "UnkTargetBase.h"

// declared: 0x00024E60 Unk_00026240::FUN_00124940
// declared: 0x00024B40 Unk_00026240::FUN_00124980

struct ERC;

struct Counted_00026240
{
    void FUN_001350C0();
};

// A sign-field screen. Its vtable is at 0x002E2F30 and overrides slots 0, 1 and 2 of UnkTargetBase.
// The call in the constructor is InitSignField, 0x000248B0.
class Unk_00026240 : public UnkTargetBase
{
public:
    Unk_00026240();
    virtual ~Unk_00026240();
    virtual void FUN_00124940();
    virtual void FUN_00124980(ERC* rc);

    void FUN_000248B0();

    char pad44[0x7C - 0x44];
    Counted_00026240* unk7C;
    Counted_00026240* unk80;
    Counted_00026240* unk84;
    Counted_00026240* unk88;
};

// 0x00026240
Unk_00026240::Unk_00026240()
{
    FUN_000248B0();
}

// 0x00026290
Unk_00026240::~Unk_00026240()
{
    unk7C->FUN_001350C0();
    unk7C = 0;
    unk80->FUN_001350C0();
    unk80 = 0;
    unk84->FUN_001350C0();
    unk84 = 0;
    unk88->FUN_001350C0();
    unk88 = 0;
}
