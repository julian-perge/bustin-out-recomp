#include "UnkTargetBase.h"

// generated: 0x0003B2D0
// generated: 0x0003B2E0
// generated: 0x0003B2F0
// generated: 0x0003B360

extern "C" void* memset(void* dest, int c, unsigned int count);

struct ERC;

struct ListBase_0003B940
{
    ~ListBase_0003B940() { FUN_00142B90(); }
    void FUN_00142B90();

    void* head;
    void* tail;
    char owns;
};

struct List_0003B940 : ListBase_0003B940
{
    List_0003B940()
    {
        tail = 0;
        head = 0;
        owns = 1;
    }
};

// The destructor of Unk80026864 unwinds its two lists through two different destructor thunks,
// 0x00035E50 and 0x00035E60, so the lists are two types.
struct OwnedList_0003B940 : ListBase_0003B940
{
    OwnedList_0003B940()
    {
        tail = 0;
        head = 0;
        owns = 1;
    }
};

struct Words_0003B940
{
    Words_0003B940() { Clear(); }
    void Clear()
    {
        unk0 = 0;
        unk4 = 0;
        unk8 = 0;
        unkC = 0;
        unk10 = 0;
        unk14 = 0;
        unk18 = 0;
        unk1C = 0;
        unk20 = 0;
        unk24 = 0;
    }
    int unk0, unk4, unk8, unkC, unk10, unk14, unk18, unk1C, unk20, unk24;
};

struct Child_0003B940
{
    void FUN_000574F0();
};

struct TilePair_0003B940
{
    int unk0;
    int unk4;
};

class Obj_0003B940
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
    virtual void vfn20();
    virtual void vfn21();
    virtual void vfn22();
    virtual void vfn23();
    virtual void vfn24();
    virtual void vfn25();
    virtual void vfn26();
    virtual void vfn27();
    virtual void vfn28();
    virtual void vfn29();
    virtual void vfn30();
    virtual void vfn31();
    virtual void vfn32();
    virtual void vfn33();
    virtual void vfn34();
    virtual void vfn35();
    virtual void vfn36();
    virtual void vfn37();
    virtual void vfn38();
    virtual void vfn39();
    virtual void vfn40();
    virtual void vfn41();
    virtual void vfn42();
    virtual void vfn43();
    virtual void vfn44();
    virtual void vfn45();
    virtual void vfn46();
    virtual void vfn47();
    virtual void vfn48();
    virtual void vfn49();
    virtual void vfn50();
    virtual void vfn51();
    virtual void vfn52();
    virtual char vfn53();
    virtual void vfn54();
    virtual void vfn55();
    virtual void vfn56();
    virtual void vfn57();
    virtual void vfn58();
    virtual void vfn59();
    virtual void vfn60();
    virtual void vfn61();
    virtual void vfn62();
    virtual void vfn63();
    virtual void vfn64();
    virtual void vfn65();
    virtual void vfn66();
    virtual void vfn67();
    virtual void vfn68();
    virtual void vfn69();
    virtual void vfn70();
    virtual void vfn71();
    virtual void vfn72();
    virtual void vfn73();
    virtual void vfn74();
    virtual void vfn75();
    virtual void vfn76();
    virtual void vfn77();
    virtual void vfn78();
    virtual void vfn79();
    virtual void vfn80();
    virtual void vfn81();
    virtual void vfn82();
    virtual void vfn83();
    virtual void vfn84();
    virtual void vfn85();
    virtual void vfn86();
    virtual short vfn87(int a);
    virtual void vfn88();
    virtual void vfn89();
    virtual void vfn90();
    virtual void vfn91();
    virtual void vfn92();
    virtual void vfn93();
    virtual void vfn94();
    virtual void vfn95();
    virtual void vfn96();
    virtual void vfn97();
    virtual void vfn98();
    virtual void vfn99();
    virtual void vfn100();
    virtual void vfn101();
    virtual void vfn102();
    virtual void vfn103();
    virtual void vfn104();
    virtual void vfn105();
    virtual void vfn106();
    virtual void vfn107();
    virtual void vfn108();
    virtual void vfn109();
    virtual int vfn110();
    virtual void vfn111();
    virtual void vfn112();
    virtual TilePair_0003B940* vfn113();
    virtual void vfn114();
    virtual void vfn115();
    virtual void vfn116();
    virtual void vfn117();
    virtual void vfn118();
    virtual void vfn119();
    virtual void vfn120();
    virtual void vfn121();
    virtual void vfn122();
    virtual char vfn123();
};

class Manager_0003B940
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
    virtual Obj_0003B940* vfn18(int id);
};

class Factory_0003B940
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
    virtual int vfn13(int id);
};

class Obj47_0003B940
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
    virtual void vfn20();
    virtual void vfn21();
    virtual void vfn22();
    virtual void vfn23();
    virtual void vfn24();
    virtual void vfn25();
    virtual void vfn26();
    virtual void vfn27();
    virtual void vfn28();
    virtual void vfn29();
    virtual void vfn30();
    virtual void vfn31();
    virtual void vfn32();
    virtual void vfn33();
    virtual void vfn34();
    virtual void vfn35();
    virtual void vfn36();
    virtual void vfn37();
    virtual void vfn38();
    virtual void vfn39();
    virtual void vfn40();
    virtual void vfn41();
    virtual void vfn42();
    virtual void vfn43();
    virtual void vfn44();
    virtual void vfn45();
    virtual void vfn46();
    virtual void vfn47();
};

struct NodeBase_0003B940
{
    int unk0;
};

class Node_0003B940 : public virtual NodeBase_0003B940, public virtual Obj_0003B940
{
};

class Part_0003B940 : public virtual NodeBase_0003B940, public virtual Obj47_0003B940
{
public:
    virtual void pfn0();
    virtual void pfn1();
    virtual void pfn2();
    virtual void pfn3();
    virtual void pfn4();
    virtual void pfn5();
    virtual void pfn6();
    virtual int pfn7();

    Node_0003B940* unk8;
};

struct Camera_0003B940
{
    void FUN_000894C0();
};

struct Hud_0003B940
{
    char pad0[4];
    Camera_0003B940* unk4;
};

struct Sound_0003B940
{
    void FUN_0006B050(unsigned int name);
};

struct Locator_0003B940
{
    bool FUN_000703D0();
};

struct Players_0003B940
{
    bool FUN_0006F140(char player);
};

struct Options_0003B940
{
    char pad0[0x101];
    char unk101;
};

Part_0003B940* FUN_00038B40(Obj_0003B940* object, int kind);
short FUN_001B7BC0(Manager_0003B940* manager, int a, int b, int c);

extern Manager_0003B940* DAT_003DCEB0;
extern Factory_0003B940* DAT_003DCEA4;
extern Hud_0003B940* DAT_00310C48;
extern Sound_0003B940* DAT_00310B3C;
extern Locator_0003B940 DAT_00310B98;
extern Players_0003B940* DAT_0030FEC0;
extern Options_0003B940* DAT_00310CAC;
extern int DAT_00310CCC;

class Unk80026864;
typedef int (Unk80026864::*Unk80026864Handler)();

class Unk80026864 : public UnkTargetBase, public virtual Unk802A2AC0
{
public:
    Unk80026864(int player);
    virtual ~Unk80026864();
    virtual void FUN_00124940();
    virtual void FUN_00124980(ERC* rc);
    virtual void FUN_00124700(const EVec3* position);
    virtual void FUN_00017C90(int sender, int message);
    virtual void FUN_000365B0(unsigned int bits, bool set);
    virtual void SetMode(int newMode);
    virtual void vfn2(int a1, int a2);

    void FUN_00038CA0(int a);
    void FUN_0003A4A0();
    void FUN_0003A8F0();
    void FUN_0003C510();
    void FUN_00040D60();
    void FUN_0003EA70();
    void FUN_0003EEB0();
    int FUN_00036A50();
    int FUN_0003E6F0();
    int FUN_00040BF0();
    int FUN_00040810();
    int FUN_00042A60();
    static void FUN_0003B8D0();

    bool IsBuildMode() const { return mode == 8 || mode == 10 || mode == 11 || mode == 9; }

    Unk80026864Handler unk50[7];
    unsigned int unkA4;
    int unkA8;
    char unkAC;
    char unkAD;
    EVec3 unkB0;
    EVec3 unkBC;
    float unkC8;
    float unkCC;
    EVec2 unkD0;
    int unkD8;
    void* unkDC;
    void* unkE0;
    Child_0003B940* unkE4;
    char unkE8;
    float unkEC;
    float unkF0;
    float unkF4;
    float unkF8;
    float unkFC;
    float unk100;
    unsigned short unk104;
    int unk108;
    Part_0003B940* unk10C;
    float unk110;
    char unk114;
    void* unk118;
    void* unk11C;
    void* unk120;
    void* unk124;
    void* unk128;
    void* unk12C;
    void* unk130;
    void* unk134;
    void* unk138;
    void* unk13C;
    void* unk140;
    void* unk144;
    void* unk148;
    void* unk14C;
    void* unk150;
    void* unk154;
    void* unk158;
    int unk15C;
    int unk160;
    List_0003B940 unk164;
    Words_0003B940 unk170;
    char pad198[0xC];
    EVec3 unk1A4;
    OwnedList_0003B940 unk1B0;
    void* unk1BC;
    TilePair_0003B940 unk1C0;
    short unk1C8;
    int unk1CC;
    int unk1D0;
    int unk1D4;
    float unk1D8;
    int unk1DC;
    int unk1E0;
};

struct Defaults_0003B940
{
    int words[10];
};

typedef void (*Callback_0003B940)();

void FUN_0003A0E0();
void FUN_00038320();
void FUN_00038500();
void FUN_00038640();
void FUN_00038710();
void FUN_0003A180();
void FUN_000387E0();
void FUN_0003B8B0();
void FUN_00038A70();

extern const Defaults_0003B940 DAT_00308C9C;
extern Defaults_0003B940 DAT_003DD554;
extern Callback_0003B940 DAT_003DD52C[9];

// 0x0003B8D0
void Unk80026864::FUN_0003B8D0()
{
    DAT_003DD554 = DAT_00308C9C;
    DAT_003DD52C[0] = FUN_0003A0E0;
    DAT_003DD52C[1] = FUN_00038320;
    DAT_003DD52C[2] = FUN_00038500;
    DAT_003DD52C[3] = FUN_00038640;
    DAT_003DD52C[4] = FUN_00038710;
    DAT_003DD52C[5] = FUN_0003A180;
    DAT_003DD52C[6] = FUN_000387E0;
    DAT_003DD52C[7] = FUN_0003B8B0;
    DAT_003DD52C[8] = FUN_00038A70;
}

// 0x0003B940
Unk80026864::Unk80026864(int player)
{
    FUN_0003B8D0();
    this->player = player;
    unkBC = EVec3(0.0f);
    unkB0 = unkBC;
    unkDC = 0;
    unkE0 = 0;
    unkE4 = 0;
    unk118 = 0;
    unk11C = 0;
    unk120 = 0;
    unk124 = 0;
    unk128 = 0;
    unk12C = 0;
    unk130 = 0;
    unk134 = 0;
    unk138 = 0;
    unk13C = 0;
    unk140 = 0;
    unk144 = 0;
    unk14C = 0;
    unk148 = 0;
    unk150 = 0;
    unk154 = 0;
    unk158 = 0;
    unk15C = 0;
    unk160 = 0;
    unkD8 = 0;
    unk10C = 0;
    unkA4 = 0;
    unkA8 = 0;
    unkAD = 0;
    unkAC = 0;
    unk110 = 0.0f;
    unk1CC = 0;
    unk1D8 = 0.0f;
    unk1D0 = 0;
    unk1D4 = 1;
    unk114 = 0;
    unk1DC = 1;
    memset(unk50, 0, sizeof(unk50));
    unk50[0] = &Unk80026864::FUN_00036A50;
    unk50[2] = &Unk80026864::FUN_0003E6F0;
    unk50[3] = &Unk80026864::FUN_00040BF0;
    unk50[4] = &Unk80026864::FUN_00040810;
    unk50[5] = &Unk80026864::FUN_00042A60;
    unkE8 = 0;
}

// 0x0003B230
Unk80026864::~Unk80026864()
{
    FUN_0003A4A0();
}

// 0x000365B0
void Unk80026864::FUN_000365B0(unsigned int bits, bool set)
{
    if (set) {
        flags |= bits;
    } else {
        flags &= ~bits;
    }
}

// 0x00036570
void Unk80026864::FUN_00124700(const EVec3* position)
{
    unkBC = *position;
    parent->FUN_00017C90((int)this, player == 0 ? 0x15 : 0x16);
}

// 0x0003B2C0
void Unk80026864::FUN_00124980(ERC* rc)
{
}

// 0x0003B300
void Unk80026864::vfn2(int a1, int a2)
{
}

// 0x00036670
void Unk80026864::SetMode(int newMode)
{
    mode = newMode;
    switch (newMode) {
    case 9:
        FUN_00124680(2, 1);
        break;
    case 0:
        FUN_00040D60();
        FUN_0003EA70();
        FUN_0003EEB0();
        unkE4->FUN_000574F0();
        unkA4 = 0;
        SetFlags(2, true);
        break;
    case 8:
        FUN_00040D60();
        FUN_0003EA70();
        FUN_0003EEB0();
        unkE4->FUN_000574F0();
        FUN_00124680(2, 0);
        unkA4 = 6;
        break;
    case 3:
        if (player == 0) {
            FUN_00040D60();
            FUN_0003EA70();
            FUN_0003EEB0();
            unkE4->FUN_000574F0();
            FUN_00124680(2, 0);
            unkA4 = 0;
        }
        break;
    case 4:
        if (player != 1) {
            break;
        }
    case 1:
    case 2:
    case 6:
    case 7:
        FUN_00040D60();
        FUN_0003EA70();
        FUN_0003EEB0();
        unkE4->FUN_000574F0();
        FUN_00124680(2, 0);
        unkA4 = 0;
        break;
    case 5:
        break;
    default:
        FUN_00040D60();
        FUN_0003EA70();
        FUN_0003EEB0();
        break;
    }
}

// 0x0003C620
void Unk80026864::FUN_00124940()
{
    if (player == 1 && !DAT_00310B98.FUN_000703D0()) {
        return;
    }
    if (DAT_0030FEC0->FUN_0006F140(player) && Flag1() && DAT_00310CAC->unk101 == 0) {
        switch (mode) {
        case 0:
        case 1:
        case 2:
        case 3:
        case 4:
        case 5:
        case 6:
        case 7:
            FUN_0003A8F0();
            break;
        case 9:
            if (player == DAT_00310CCC) {
                FUN_0003C510();
            }
            break;
        }
    }
}

// 0x00038D00
void Unk80026864::FUN_00017C90(int sender, int message)
{
    if (message == 0x1D) {
        if (!IsBuildMode()) {
            parent->FUN_00017C90((int)this, 0x14);
            DAT_00310C48->unk4->FUN_000894C0();
            unkA4 = 0;
        } else {
            unkE4->FUN_000574F0();
            unkA4 = 0;
        }
    } else if (message == 0x1C) {
        if (IsBuildMode()) {
            Obj_0003B940* object = DAT_003DCEB0->vfn18(sender);
            if (object && object->vfn123()) {
                if (FUN_00038B40(object, 8)->unk8 != 0) {
                    object = FUN_00038B40(object, 8)->unk8;
                }
            }
            if (object && object->vfn53()) {
                unk1CC = 0;
                unkAD = 0;
                unkAC = 1;
                unk1C0 = *object->vfn113();
                unk1C8 = object->vfn87(1);
                int arg = DAT_003DCEA4->vfn13(0x437);
                Manager_0003B940* manager = DAT_003DCEB0;
                short id = FUN_001B7BC0(manager, object->vfn110(), arg, 1);
                unk10C = FUN_00038B40(DAT_003DCEB0->vfn18(id), 4);
                unk10C->vfn47();
                if (unk10C != 0) {
                    DAT_00310B3C->FUN_0006B050(0xD9552AE4);
                    unkE4->FUN_000574F0();
                    unkA4 = 0;
                    FUN_00038CA0(unk10C->pfn7());
                    return;
                }
                DAT_00310B3C->FUN_0006B050(0x3804219F);
                return;
            }
            DAT_00310B3C->FUN_0006B050(0x3804219F);
        }
    } else {
        if (message == 0x1A) {
            message = 0x11;
        } else if (message == 0x1B) {
            message = 0x12;
        }
        parent->FUN_00017C90(sender, message);
    }
}
