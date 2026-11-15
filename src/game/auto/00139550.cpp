#include "UnkTargetBase.h"

// declared: 0x001397B0 Unk_00139550::FUN_00124940

struct Counted_00139550
{
    void FUN_001350C0();
};

// A member with only a virtual destructor. Its vtable is at 0x002E3460.
class Tag_00139550
{
public:
    virtual ~Tag_00139550() {}
};

// A screen with two counted objects. Its vtable is at 0x002ED2B8: it overrides slots 0 and 1 of
// UnkTargetBase and adds slots 17 and 18.
class Unk_00139550 : public UnkTargetBase
{
public:
    virtual ~Unk_00139550();
    virtual void FUN_00124940();
    virtual void FUN_00139780();
    virtual void FUN_00139E30();

    Tag_00139550 unk44;
    char pad48[0x74 - 0x48];
    Counted_00139550* unk74;
    Counted_00139550* unk78;
};

// 0x00139550
Unk_00139550::~Unk_00139550()
{
    if (unk74) {
        unk74->FUN_001350C0();
    }
    if (unk78) {
        unk78->FUN_001350C0();
    }
    unk74 = 0;
    unk78 = 0;
}
