#include "UnkTargetBase.h"

// declared: 0x000A1B00 S_000A1B00::S_000A1B00
// declared: 0x000A0DD0 S_000A1B00::~S_000A1B00
// declared: 0x0009F540 S_0009F540::S_0009F540
// declared: 0x0009BAB0 S_0009F540::~S_0009F540
// declared: 0x000A8720 S_000A80B0::FUN_00124940
// declared: 0x000ADA10 S_000A80B0::FUN_00124980
// declared: 0x000A8CC0 S_000A80B0::FUN_00017C90
// declared: 0x000A9CF0 S_000A80B0::FUN_00017CB0
// declared: 0x000AAEC0 S_000A80B0::FUN_00017CC0

// generated: 0x000ACA10
// generated: 0x000ACA20
// generated: 0x000ACA30
// generated: 0x000ACB50

struct ERC;

// The buy menu. Its largest member offset is a byte at +0x1218, and the gap to the build menu in
// the pause screen is 0x121C.
class S_000A1B00 : public S_00145A00
{
public:
    S_000A1B00();
    virtual ~S_000A1B00();

    void FUN_000A0A10();
    void FUN_000A0970(unsigned char a);
    void FUN_000A09C0(int a);
    void FUN_000A0CA0();
    void FUN_000A0E40();

    char unkF4[0x121C - 0xF4];
};

// The build menu. Its largest member offset is a byte at +0x1220, and the pause screen has its
// next member 0x1224 bytes after it.
class S_0009F540 : public S_00145A00
{
public:
    S_0009F540();
    virtual ~S_0009F540();

    void FUN_0009AB20(unsigned char a);
    void FUN_0009AB30(int a);
    void FUN_0009AB90();
    void FUN_0009B3C0();
    void FUN_0009BB20();

    char unkF4[0x1224 - 0xF4];
};

class Owned_000A80B0
{
public:
    virtual ~Owned_000A80B0();
};

struct Counted_000A80B0
{
    void FUN_001350C0();
};

class S_000A80B0;

struct Flash_000A80B0
{
    void FUN_000FE8D0(S_000A80B0* screen);
};

void FUN_000A2A50();

extern Flash_000A80B0* DAT_00310C28;

class S_000A80B0 : public UnkTargetBase, public virtual Unk802A2AC0
{
public:
    S_000A80B0();
    virtual ~S_000A80B0();
    virtual void FUN_00124940();
    virtual void FUN_00124980(ERC* rc);
    virtual void FUN_00017C90(int sender, int message);
    virtual void FUN_00017CB0(int a1, int a2);
    virtual int FUN_00017CC0(int a1);
    virtual void SetMode(int newMode);
    virtual void vfn2(int a1, int a2);
    virtual void FUN_000A82C0();
    virtual void FUN_000A8C40();

    char unk48[0x6C - 0x48];
    S_000A1B00 buy;
    S_0009F540 build;
    Owned_000A80B0* unk24AC;
    int unk24B0;
    Counted_000A80B0* unk24B4;
    int unk24B8;
    int unk24BC;
    int unk24C0;
    Owned_000A80B0* unk24C4;
    int unk24C8;
    int unk24CC;
    char unk24D0[0x25A8 - 0x24D0];
};

// 0x000A80B0
S_000A80B0::S_000A80B0()
{
    unk24B4 = 0;
    unk24AC = 0;
    unk24CC = 0;
}

// 0x000ACA40
S_000A80B0::~S_000A80B0()
{
    FUN_000A8C40();
}

// 0x000A8180
void S_000A80B0::SetMode(int newMode)
{
    mode = newMode;
    switch (newMode) {
    case 8:
    case 10:
    case 11:
        if (unk24BC == 4) {
            buy.FUN_00124680(4, true);
            buy.FUN_000A0A10();
            buy.FUN_000A0970(0);
        } else if (unk24BC == 5) {
            build.FUN_00124680(4, true);
            build.FUN_0009AB90();
            build.FUN_0009AB20(0);
        } else if (unk24BC != 12) {
            if (unk24BC == 0) {
                unk24BC = 1;
            }
        }
        break;
    }
}

// 0x000A8220
void S_000A80B0::vfn2(int a1, int a2)
{
    switch (a1) {
    case 0:
        buy.FUN_000A0CA0();
        buy.FUN_000A0E40();
        build.FUN_0009B3C0();
        build.FUN_0009BB20();
        FUN_000A8C40();
        FUN_000A82C0();
        SetMode(8);
        break;
    case 1:
        buy.FUN_000A09C0(a2);
        build.FUN_0009AB30(a2);
        break;
    }
}

// 0x000A8C40
void S_000A80B0::FUN_000A8C40()
{
    if (unk24B4) {
        unk24B4->FUN_001350C0();
        unk24B4 = 0;
    }
    FUN_001247E0(&buy);
    FUN_001247E0(&build);
    FUN_000A2A50();
    if (unk24AC) {
        delete unk24AC;
        unk24AC = 0;
    }
    delete unk24C4;
    unk24C4 = 0;
    DAT_00310C28->FUN_000FE8D0(this);
}
