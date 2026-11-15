#include "UnkTargetBase.h"

// declared: 0x00159FE0 Panel_000BD710::~Panel_000BD710
// declared: 0x00058000 Panel_000BD710::FUN_00124700
// declared: 0x00058020 Panel_000BD710::FUN_00017CD0
// declared: 0x0015A060 Panel_000BD710::FUN_00145550
// declared: 0x0015A4B0 Panel_000BD710::FUN_00145830
// declared: 0x0015A9F0 Panel_000BD710::FUN_00146280
// declared: 0x00058040 Panel_000BD710::FUN_00146240
// declared: 0x00058050 Panel_000BD710::FUN_00146250
// declared: 0x0015A3F0 Panel_000BD710::Panel_000BD710
// declared: 0x000BD5E0 PanelChild_000BD710::~PanelChild_000BD710
// declared: 0x000BDDB0 PanelChild_000BD710::FUN_00124940
// declared: 0x000BAFF0 PanelChild_000BD710::FUN_00124980
// declared: 0x000BB6C0 Unk_000BD710::FUN_00124940
// declared: 0x000BCEE0 Unk_000BD710::FUN_00124980
// declared: 0x000BAC40 Unk_000BD710::SetMode
// declared: 0x000BD900 Unk_000BD710::vfn2

// generated: 0x000BD8D0
// generated: 0x000BDAF0

struct ERC;

struct Slot_000BD710
{
    char unk0[0x20];
};

extern Slot_000BD710 DAT_00321760[];
extern const float DAT_002E33F8;
extern const float DAT_002E2394;
extern const float DAT_002E2514;

// The class that the per-player screen holds as a member. It derives from S_00145A00, and the
// constructor 0x0015A3F0 builds it from eight arguments.
class Panel_000BD710 : public S_00145A00
{
public:
    Panel_000BD710(int a1, int a2, float a3, float a4, float a5, int a6, int a7, bool a8);
    virtual ~Panel_000BD710();
    virtual void FUN_00124700(const EVec3* position);
    virtual void FUN_00017CD0(int a1, int a2);
    virtual void FUN_00145550();
    virtual void FUN_00145830(int a1, int a2, int a3, int a4);
    virtual void FUN_00146280();
    virtual void FUN_00146240();
    virtual void FUN_00146250();

    int unkF4;
    void* unkF8;
    void* unkFC;
    int unk100;
    float unk104;
    bool unk108;
};

// The panel with its own destructor 0x000BD5E0, built inline in the constructor of the screen.
class PanelChild_000BD710 : public Panel_000BD710
{
public:
    PanelChild_000BD710(int a1, int a2, float a3, float a4, float a5, int a6, int a7, bool a8)
        : Panel_000BD710(a1, a2, a3, a4, a5, a6, a7, a8)
    {
        unk110 = 0;
        unk114 = 0;
        unk118 = 0;
        unk10C = 0;
    }
    virtual ~PanelChild_000BD710();
    virtual void FUN_00124940();
    virtual void FUN_00124980(ERC* rc);

    int unk10C;
    int unk110;
    int unk114;
    int unk118;
};

// The per-player screen that holds a panel. Its vtable is at 0x002E8378 and its virtual base is
// at +0x19C.
class Unk_000BD710 : public UnkTargetBase, public virtual Unk802A2AC0
{
public:
    Unk_000BD710(int player);
    virtual ~Unk_000BD710();
    virtual void FUN_00124940();
    virtual void FUN_00124980(ERC* rc);
    virtual void SetMode(int newMode);
    virtual void vfn2(int a1, int a2);

    void FUN_000BA740(Slot_000BD710* slot, int a2);

    PanelChild_000BD710 unk48;
    float unk164;
    float unk168;
    int unk16C;
    int unk170;
    char pad174[4];
    float unk178;
    float unk17C;
    float unk180;
    float unk184;
    float unk188;
    float unk18C;
    float unk190;
    int unk194;
};

// 0x000BD710
// parked: scheduling
Unk_000BD710::Unk_000BD710(int player) : unk48(-1, -1, 0.05f, 0.0f, 0.0f, -1, -1, true)
{
    float zero = 0.0f;
    float one = DAT_002E33F8;
    float two = DAT_002E2394;
    unk178 = one;
    unk17C = one;
    unk184 = unk188 = unk18C = zero;
    unk180 = two;
    unk164 = zero;
    unk168 = zero;
    unk16C = 0;
    this->player = player;
    SetFlags(2, false);
    zero = 0.0f;
    unk184 = unk188 = unk18C = zero;
    one = DAT_002E33F8;
    unk178 = one;
    unk17C = one;
    unk180 = DAT_002E2394;
    unk194 = 0;
    unk170 = 0;
    unk190 = DAT_002E2514;
    FUN_000BA740(&DAT_00321760[this->player], 1);
}

// 0x000BD910
Unk_000BD710::~Unk_000BD710()
{
}
