#include "UnkTargetBase.h"

// declared: 0x00127860 Tracked_000B7340::~Tracked_000B7340
// declared: 0x000B73A0 Unk_000B7340::FUN_00124940
// declared: 0x000B75F0 Unk_000B7340::FUN_00124980

struct ERC;

void FUN_00123040(void* p);

// A class with a vtable at 0x002ECA00 that clears the two globals at 0x0035D420 and 0x0035D424
// when they point at it.
class Tracked_000B7340
{
public:
    virtual ~Tracked_000B7340();
    virtual void vfn1();
    virtual void vfn2();
    virtual void vfn3();
    virtual void vfn4();
    virtual void vfn5();
    virtual void vfn6();
};

// A screen with a tracked object at +0x44. Its vtable is at 0x002E8038 and overrides slots 0, 1 and
// 2 of UnkTargetBase.
class Unk_000B7340 : public UnkTargetBase
{
public:
    virtual ~Unk_000B7340();
    virtual void FUN_00124940();
    virtual void FUN_00124980(ERC* rc);

    void operator delete(void* p) { FUN_00123040(p); }

    Tracked_000B7340 unk44;
};

// 0x000B7340
Unk_000B7340::~Unk_000B7340()
{
}
