#include "UnkTargetBase.h"

// declared: 0x00053BD0 Unk_00053DD0::~Unk_00053DD0
// declared: 0x00053F10 Unk_00053DD0::FUN_00124940
// declared: 0x000527A0 Unk_00053DD0::FUN_00124980
// declared: 0x00052930 Unk_00053DD0::FUN_00017C90
// declared: 0x00053D40 Unk_00053DD0::FUN_001247C0
// declared: 0x000522D0 Unk_00053DD0::FUN_00145D30
// declared: 0x00052380 Unk_00053DD0::FUN_00145830
// declared: 0x000529C0 Unk_00053DD0::FUN_00146280
// declared: 0x00052740 Unk_00053DD0::FUN_00146240
// declared: 0x00052770 Unk_00053DD0::FUN_00146250
// declared: 0x00050E30 Unk_00053DD0::SetMode
// declared: 0x00053D30 Unk_00053DD0::vfn2

// generated: 0x00053D00
// generated: 0x00053EE0

struct ERC;

class Unk_00053DD0;

extern Unk_00053DD0* DAT_003106A0;

// 0x000136D0 is the operator new of the game. The symbol list does not name it yet, so it is
// called through the class's own operator new.
void* FUN_000136D0(unsigned int size);

// An object of 0x14 bytes that the constructor makes with operator new.
struct Pool_00053DD0
{
    Pool_00053DD0()
    {
        unkC = 0;
        unk8 = 0;
        unk10 = 1;
        unk4 = 0;
    }

    void* operator new(unsigned int size) { return FUN_000136D0(size); }

    int unk0;
    int unk4;
    int unk8;
    int unkC;
    char unk10;
};

// The per-player screen that derives from S_00145A00. Its vtable is at 0x002E4048 and its virtual
// base is at +0x320.
class Unk_00053DD0 : public S_00145A00, public virtual Unk802A2AC0
{
public:
    Unk_00053DD0(int player);
    virtual ~Unk_00053DD0();
    virtual void FUN_00124940();
    virtual void FUN_00124980(ERC* rc);
    virtual void FUN_00017C90(int sender, int message);
    virtual void FUN_001247C0(UnkTargetBase* child);
    virtual void FUN_00145D30(int a1);
    virtual void FUN_00145830(int a1, int a2, int a3, int a4);
    virtual void FUN_00146280();
    virtual void FUN_00146240();
    virtual void FUN_00146250();
    virtual void FUN_00054520();
    virtual void SetMode(int newMode);
    virtual void vfn2(int a1, int a2);

    bool unkF8;
    bool unkF9;
    char padFA[0x108 - 0xFA];
    Pool_00053DD0* unk108;
    int unk10C;
    int unk110;
    char pad114[0x118 - 0x114];
    int unk118;
    char pad11C[0x320 - 0x11C - 4];
};

// 0x00053DD0
Unk_00053DD0::Unk_00053DD0(int player) : S_00145A00(-1, 0, 0.05f, 0.0f, 0.0f)
{
    this->player = player;
    unkF8 = true;
    unkF9 = false;
    unk108 = new Pool_00053DD0;
    unk118 = 0;
    unk110 = 0;
    unk10C = 0;
    if (player == 0) {
        DAT_003106A0 = this;
    }
}
