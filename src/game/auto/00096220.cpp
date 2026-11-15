#include "UnkTargetBase.h"

// declared: 0x000ACA40 Pause_00096220::~Pause_00096220
// declared: 0x00097AC0 Load_00096220::~Load_00096220
// declared: 0x00095080 Hud_00096220::FUN_00124940
// declared: 0x00094A00 Hud_00096220::FUN_00124980
// declared: 0x00090310 Hud_00096220::FUN_00017C90
// declared: 0x00092E40 Hud_00096220::FUN_00017CB0
// declared: 0x00096340 Hud_00096220::FUN_00017CC0

struct ERC;

void FUN_00123040(void* p);

// The pause screen, class 3 of the thunk trial (0x000A80B0), which the HUD holds as a member. Only
// what the destructor of the HUD needs is declared.
class Pause_00096220 : public UnkTargetBase, public virtual Unk802A2AC0
{
public:
    virtual ~Pause_00096220();
    virtual void SetMode(int newMode);
    virtual void vfn2(int a1, int a2);

    char pad48[0x25A8 - 0x48];
};

// The class built on the virtual base alone (0x00097AC0), which the HUD holds as a member.
class Load_00096220 : public Unk802A2AC0
{
public:
    virtual ~Load_00096220();
    virtual void SetMode(int newMode);
    virtual void vfn2(int a1, int a2);
};

// The HUD screen (F-0042). Its vtable is at 0x002E6888 and overrides slots 0, 1, 2, 6, 7 and 8 of
// UnkTargetBase. The call in the destructor is ShutdownHUD, 0x0008FEE0.
class Hud_00096220 : public UnkTargetBase
{
public:
    virtual ~Hud_00096220();
    virtual void FUN_00124940();
    virtual void FUN_00124980(ERC* rc);
    virtual void FUN_00017C90(int sender, int message);
    virtual void FUN_00017CB0(int a1, int a2);
    virtual int FUN_00017CC0(int a1);

    void operator delete(void* p) { FUN_00123040(p); }

    void FUN_0008FEE0();

    char pad44[0x15C - 0x44];
    Pause_00096220 unk15C;
    char pad2710[0x2728 - 0x2710];
    Load_00096220 unk2728;
};

// 0x00096220
Hud_00096220::~Hud_00096220()
{
    FUN_0008FEE0();
}
