#include "UnkTargetBase.h"

// declared: 0x000AF7C0 Unk_000AF6F0::FUN_00124940
// declared: 0x000AF7D0 Unk_000AF6F0::FUN_00124980

struct ERC;

struct Counted_000AF6F0
{
    void FUN_001350C0();
};

// A screen with three owned objects. Its vtable is at 0x002E7C00 and has 19 slots: it overrides
// slots 0, 1 and 2 of UnkTargetBase and adds slots 17 and 18.
class Unk_000AF6F0 : public UnkTargetBase
{
public:
    Unk_000AF6F0();
    virtual ~Unk_000AF6F0();
    virtual void FUN_00124940();
    virtual void FUN_00124980(ERC* rc);
    virtual void FUN_000AF720();
    virtual void FUN_000AF780();

    int unk44;
    int unk48;
    int unk4C;
    char pad50[0x5C - 0x50];
    float unk5C;
    float unk60;
    Counted_000AF6F0* unk64;
    Counted_000AF6F0* unk68;
};

// 0x000AF6F0
Unk_000AF6F0::Unk_000AF6F0()
{
    unk44 = 0;
    unk4C = 0;
    unk68 = 0;
    unk64 = 0;
    unk48 = 0;
}

// 0x000AF780
void Unk_000AF6F0::FUN_000AF780()
{
    if (unk64) {
        unk64->FUN_001350C0();
        unk64 = 0;
    }
    if (unk44) {
        FUN_00124810();
    }
    if (unk68) {
        unk68->FUN_001350C0();
        unk68 = 0;
    }
}

// 0x000AF910
Unk_000AF6F0::~Unk_000AF6F0()
{
    FUN_000AF780();
}
