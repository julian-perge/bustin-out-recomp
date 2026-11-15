#include "UnkTargetBase.h"

// declared: 0x00097B10 Unk_00097AC0::SetMode
// declared: 0x00097AB0 Unk_00097AC0::vfn2

// A class built on the virtual base alone, with no UnkTargetBase. Its vtable is at 0x002E6B44. It
// overrides both slots of Unk802A2AC0, and it is the member at +0x2728 of the HUD screen.
class Unk_00097AC0 : public Unk802A2AC0
{
public:
    virtual ~Unk_00097AC0();
    virtual void SetMode(int newMode);
    virtual void vfn2(int a1, int a2);

    void FUN_00097880();
};

// 0x00097AC0
Unk_00097AC0::~Unk_00097AC0()
{
    FUN_00097880();
}
