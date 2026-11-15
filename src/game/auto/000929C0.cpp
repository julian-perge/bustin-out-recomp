#include "UnkTargetBase.h"

// declared: 0x000141B0 Unk_000929C0::SetMode
// declared: 0x00092990 Unk_000929C0::vfn2

void FUN_00123040(void* p);

// The destructor of this class is 0x00127860 (it clears the two globals at 0x0035D420 and
// 0x0035D424 when they point at it). The unwind code calls it through a jump at 0x00018810, so the
// destructor is a one-line forwarder in the source.
struct Tracked_000929C0
{
    ~Tracked_000929C0() { FUN_00127860(); }
    void FUN_00127860();
};

// A class built on the virtual base alone, with no UnkTargetBase. Its vtable is at 0x002E6588. It
// overrides both slots of Unk802A2AC0 and adds slot 3.
class Unk_000929C0 : public Unk802A2AC0
{
public:
    virtual ~Unk_000929C0();
    virtual void SetMode(int newMode);
    virtual void vfn2(int a1, int a2);
    virtual void FUN_00017010(int a1);

    void operator delete(void* p) { FUN_00123040(p); }

    void FUN_00014190();

    int unk8;
    int unkC;
    Tracked_000929C0 unk10;
};

// 0x000929C0
Unk_000929C0::~Unk_000929C0()
{
    FUN_00014190();
}
