#include "UnkTargetBase.h"

// declared: 0x00024740 Unk_00026140::FUN_00124940
// declared: 0x00023F30 Unk_00026140::FUN_00124980

struct ERC;

void FUN_00123040(void* p);

struct Counted_00026140
{
    void FUN_001350C0();
};

// A screen that builds itself with the function at 0x00023C70. Its vtable is at 0x002E2EE8 and
// overrides slots 0, 1 and 2 of UnkTargetBase.
class Unk_00026140 : public UnkTargetBase
{
public:
    Unk_00026140();
    virtual ~Unk_00026140();
    virtual void FUN_00124940();
    virtual void FUN_00124980(ERC* rc);

    void operator delete(void* p) { FUN_00123040(p); }

    void FUN_00023C70();

    char pad44[0x78 - 0x44];
    Counted_00026140* unk78;
    char pad7C[0xD0 - 0x7C];
    Counted_00026140* unkD0;
    Counted_00026140* unkD4;
    Counted_00026140* unkD8;
};

// 0x00026140
Unk_00026140::Unk_00026140()
{
    FUN_00023C70();
}

// 0x00026190
Unk_00026140::~Unk_00026140()
{
    unkD0->FUN_001350C0();
    unkD0 = 0;
    unkD4->FUN_001350C0();
    unkD4 = 0;
    unkD8->FUN_001350C0();
    unkD8 = 0;
    unk78->FUN_001350C0();
    unk78 = 0;
}
