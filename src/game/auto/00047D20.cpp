#include "UnkTargetBase.h"

// generated: 0x00047CE0
// generated: 0x00047CF0
// generated: 0x00047D00
// generated: 0x00047ED0

extern "C" void* memset(void* dest, int c, unsigned int count);

struct ERC;

class EController
{
public:
    bool FUN_00125A00(int button);
    bool FUN_00125AD0(int button);
    float FUN_00124C40(int axis, int stick);
};

class EControllerList
{
public:
    int FUN_00125F50(int player);
    EController* FUN_00125F30(int index);
};

class ESound
{
public:
    void FUN_0006B050(unsigned int name);
};

class ELocator
{
public:
    bool FUN_000703D0();
};

class EPlayerInfo
{
public:
    virtual void vfn0();
    virtual void vfn1();
    virtual void vfn2();
    virtual void vfn3();
    virtual void vfn4();
    virtual void vfn5();
    virtual void vfn6();
    virtual void vfn7();
    virtual void vfn8();
    virtual void vfn9();
    virtual void vfn10();
    virtual void vfn11();
    virtual void vfn12();
    virtual void vfn13();
    virtual void vfn14();
    virtual void vfn15();
    virtual void vfn16();
    virtual void vfn17();
    virtual void vfn18();
    virtual void vfn19();
    virtual int vfn20();
    virtual void vfn21();
    virtual struct ECarried* vfn22();
};

struct ECarried
{
    int FUN_001C02C0();
};

class EDialogs
{
public:
    void FUN_001B91E0(int a);
    bool FUN_001B9280(int a);
};

struct EPauseHook
{
    void FUN_000E61B0();
};

struct EOptions
{
    char pad0[2];
    char kind;
};

struct EGlobalState
{
    char pad0[0x14C];
    int unk14C;
};

void FUN_001894A0(int a);
void FUN_00189480(int a);

class Unk8003AA6C;

struct EScreenSlot
{
    char pad0[0x44];
    int unk44;
    char pad48[0x10C - 0x48];
    int unk10C;
};

struct EScreens
{
    char pad0[0x148];
    Unk8003AA6C* screens[2];
    EScreenSlot* slots[2];
};

extern EControllerList* DAT_0035D3F0;
extern ESound* DAT_00310B3C;
extern ELocator DAT_00310B98;
extern EVec2 DAT_0031F810;
extern int DAT_00310CCC;
extern EPlayerInfo* DAT_00310C34[];
extern int DAT_003DCECC;
extern EScreens* DAT_00310C54;
extern char DAT_003DCEE0;
extern int DAT_003DCED4;
extern int DAT_00310CC4;
extern int DAT_003DCEDC;
extern EGlobalState* DAT_0035D3C0;
extern EDialogs* DAT_00310CB8;
extern EPauseHook DAT_00321C40;
extern EOptions* DAT_00310CB0;

class Unk8003AA6C;
typedef void (Unk8003AA6C::*Unk8003AA6CDraw)(ERC* rc, const EVec2& at);

class Unk8003AA6C : public UnkTargetBase, public virtual Unk802A2AC0
{
public:
    Unk8003AA6C(int player);
    virtual ~Unk8003AA6C();
    virtual void FUN_00124940();
    virtual void FUN_00124980(ERC* rc);
    virtual void SetMode(int newMode);
    virtual void vfn2(int a1, int a2);

    void FUN_00047B70(ERC* rc, const EVec2& at);
    void FUN_00047BD0(ERC* rc, const EVec2& at);
    void FUN_00047C10(ERC* rc, const EVec2& at);
    void FUN_00047C50(ERC* rc, const EVec2& at);
    void FUN_00047C90(ERC* rc, const EVec2& at);

    bool IsBuildMode() const { return mode == 8 || mode == 10 || mode == 11 || mode == 9; }

    EVec2 unk4C;
    Unk8003AA6CDraw draw[12];
};

// 0x00047D20
Unk8003AA6C::Unk8003AA6C(int player)
{
    unk4C = EVec2(0.0f, 0.0f);
    this->player = player;
    memset(draw, 0, sizeof(draw));
    draw[0] = &Unk8003AA6C::FUN_00047B70;
    draw[1] = &Unk8003AA6C::FUN_00047BD0;
    draw[2] = &Unk8003AA6C::FUN_00047C10;
    draw[3] = &Unk8003AA6C::FUN_00047C50;
    draw[4] = &Unk8003AA6C::FUN_00047C50;
    draw[5] = &Unk8003AA6C::FUN_00047C90;
    draw[6] = &Unk8003AA6C::FUN_00047B70;
    draw[9] = &Unk8003AA6C::FUN_00047B70;
    draw[8] = &Unk8003AA6C::FUN_00047B70;
    draw[10] = &Unk8003AA6C::FUN_00047B70;
    draw[11] = &Unk8003AA6C::FUN_00047B70;
}

// 0x000474C0
Unk8003AA6C::~Unk8003AA6C()
{
}

// 0x00047540
void Unk8003AA6C::FUN_00124940()
{
    EController* controller = DAT_0035D3F0->FUN_00125F30(DAT_0035D3F0->FUN_00125F50(player));
    if (IsBuildMode()) {
        if (player != DAT_00310CCC) {
            return;
        }
        if (mode == 9 && controller->FUN_00125A00(0x10)) {
            DAT_00310B3C->FUN_0006B050(0xD9552AE4);
            parent->FUN_00017C90((int)this, 0xD);
            return;
        }
        if (mode != 9) {
            return;
        }
        if (!controller->FUN_00125AD0(7)) {
            return;
        }
        DAT_00310B3C->FUN_0006B050(0x048AE94F);
        return;
    }
    EPlayerInfo* info = DAT_00310C34[player];
    if (mode == 2) {
        if (DAT_003DCECC) {
            if (DAT_00310C54->slots[player]->unk10C == 0) {
                DAT_00310B3C->FUN_0006B050(0x383DF7E6);
                parent->FUN_00017C90(player, 0xA);
                return;
            }
        } else if (info) {
            int a = info->vfn20();
            int b = info->vfn22()->FUN_001C02C0();
            if (a == 0 && b == 0) {
                DAT_00310B3C->FUN_0006B050(0x383DF7E6);
                parent->FUN_00017C90(player, 0xA);
                return;
            }
        }
    }
    Unk8003AA6C* other = DAT_00310C54->screens[player];
    bool otherActive = false;
    if ((player == 0 && other->mode == 3) || (player == 1 && other->mode == 4)) {
        otherActive = true;
    }
    if (mode != 1) {
        bool pause = false;
        if (((DAT_003DCEE0 && controller->FUN_00125A00(0x12)) || DAT_003DCED4) && DAT_00310CC4 != 7) {
            if (DAT_003DCEDC == 0) {
                DAT_00310CB8->FUN_001B91E0(DAT_0035D3C0->unk14C);
                if (DAT_003DCED4 == 0) {
                    FUN_001894A0(1);
                }
                pause = true;
            }
            FUN_00189480(0);
        } else {
            FUN_001894A0(0);
        }
        if (pause) {
            if (DAT_00310CB8->FUN_001B9280(-1)) {
                parent->FUN_00017C90((int)this, 0x22);
                DAT_00321C40.FUN_000E61B0();
                return;
            }
            parent->FUN_00017C90((int)this, 0x24);
            return;
        }
        if (controller->FUN_00125A00(0x10)) {
            DAT_00310B3C->FUN_0006B050(0xD9552AE4);
            parent->FUN_00017C90((int)this, 0xD);
            return;
        }
    }
    if (mode != 1 && controller->FUN_00125A00(0x12)) {
        return;
    }
    if (IsBuildMode()) {
        return;
    }
    if (mode == 1 || mode == 5) {
        return;
    }
    if (!other->Flag1() && otherActive) {
        parent->FUN_00017C90((int)this, 0x10);
        return;
    }
    if (controller->FUN_00125A00(0x14)) {
        if (mode == 3 || mode == 4) {
            return;
        }
        if (mode != 2) {
            if (DAT_00310C34[player] == 0 || DAT_00310C54->slots[player]->unk44 == 0) {
                DAT_00310B3C->FUN_0006B050(0x3804219F);
                return;
            }
        }
        DAT_00310B3C->FUN_0006B050(0x383DF7E6);
        parent->FUN_00017C90(player, 0xA);
        return;
    }
    if (mode == 2) {
        if (controller->FUN_00125A00(7) || controller->FUN_00124C40(0, 0) != 0.0f ||
            controller->FUN_00124C40(0, 1) != 0.0f) {
            DAT_00310B3C->FUN_0006B050(0x383DF7E6);
            parent->FUN_00017C90(player, 0xA);
        }
        return;
    }
    if (DAT_00310CB0->kind == 1 && controller->FUN_00125A00(0x15)) {
        DAT_00310B3C->FUN_0006B050(0x0C21C2A9);
        parent->FUN_00017C90(player, 8);
        return;
    }
    if (DAT_00310CB0->kind == 1 && controller->FUN_00125A00(0x16)) {
        DAT_00310B3C->FUN_0006B050(0x0C21C2A9);
        parent->FUN_00017C90(player, 9);
        return;
    }
    if (DAT_00310CB0->kind == 0 && controller->FUN_00125A00(0x15)) {
        DAT_00310B3C->FUN_0006B050(0x0C21C2A9);
        parent->FUN_00017C90(player, 0x2E);
        return;
    }
    if (DAT_00310CB0->kind == 0 && controller->FUN_00125A00(0x16)) {
        DAT_00310B3C->FUN_0006B050(0x0C21C2A9);
        parent->FUN_00017C90(player, 0x2F);
    }
}

// 0x00047A10
void Unk8003AA6C::FUN_00124980(ERC* rc)
{
    const EVec2* at;
    if (player == 1 && !DAT_00310B98.FUN_000703D0()) {
        return;
    }
    if (player == 1) {
        at = &EVec2(0.62f, 0.0f);
    } else if (DAT_00310B98.FUN_000703D0()) {
        at = &EVec2(0.0f, -0.74f);
    } else {
        at = &DAT_0031F810;
    }
    if (draw[mode] == 0) {
        (this->*draw[0])(rc, *at);
    } else {
        (this->*draw[mode])(rc, EVec2(at->x - 0.075f, at->y + 0.03f));
    }
}

// 0x00047520
void Unk8003AA6C::SetMode(int newMode)
{
    mode = newMode;
}

// 0x00047D10
void Unk8003AA6C::vfn2(int a1, int a2)
{
}
