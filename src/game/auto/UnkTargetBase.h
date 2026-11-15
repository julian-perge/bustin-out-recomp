#ifndef UNKTARGETBASE_H
#define UNKTARGETBASE_H

// declared: 0x001249C0 UnkTargetBase::UnkTargetBase
// declared: 0x001248B0 UnkTargetBase::~UnkTargetBase
// declared: 0x00145A00 S_00145A00::S_00145A00
// declared: 0x00145B00 S_00145A00::~S_00145A00
// declared: 0x00145BE0 S_00145A00::FUN_00124940
// declared: 0x00145710 S_00145A00::FUN_00124980
// declared: 0x001458E0 S_00145A00::FUN_00017C70
// declared: 0x001458B0 S_00145A00::FUN_00017C50
// declared: 0x00145990 S_00145A00::FUN_00017CF0
// declared: 0x00057FD0 S_00145A00::FUN_001247C0

struct EVec2
{
    float x;
    float y;
    EVec2() {}
    EVec2(float x_, float y_) { x = x_; y = y_; }
};

struct EVec3
{
    float x;
    float y;
    float z;
    EVec3() {}
    explicit EVec3(float value) { x = y = z = value; }
};

// The text member at +0x18 of UnkTargetBase. The function 0x00137AF0 points it at a shared buffer
// in the data section, and 0x001249C0 calls it. It returns nothing, so it is not a constructor. The
// wide string holder of the donor (Unk801BA678) has the same place and the same shape.
struct UnkTargetText
{
    void FUN_00137AF0();

    unsigned short* unk0;
};

// The vtable of UnkTargetBase is at 0x002EC588 and has 17 slots.
class UnkTargetBase
{
public:
    UnkTargetBase();
    virtual ~UnkTargetBase();
    virtual void FUN_00124940();
    virtual void FUN_00124980(struct ERC* rc);
    virtual void FUN_00124700(const EVec3* position);
    virtual void FUN_00017C70(const EVec2* a1);
    virtual void FUN_00017C50(const EVec3* a1);
    virtual void FUN_00017C90(int sender, int message);
    virtual void FUN_00017CB0(int a1, int a2);
    virtual int FUN_00017CC0(int a1);
    virtual void FUN_00017CD0(int a1, int a2);
    virtual void FUN_00017CE0(int a1);
    virtual void FUN_00017CF0(int a1, int a2, int a3);
    virtual EVec3* FUN_00017D00();
    virtual void FUN_001247C0(UnkTargetBase* child);
    virtual void FUN_001247E0(UnkTargetBase* child);
    virtual void FUN_001245D0(int a1, char a2);
    virtual void FUN_00124600();

    void FUN_00124680(unsigned int bits, bool set);
    void FUN_00124810();

    // The destructor destroys this member with the function at 0x00142B90.
    char children[0x0C];
    UnkTargetBase* parent;
    int unk14;
    // The constructor builds this member with the function at 0x00137AF0.
    UnkTargetText text;
    unsigned int flags;
    int unk20;
    EVec3 size;
    EVec3 position;
    int player;
    char unk40;
    char unk41;

    bool Flag1() const { return (flags >> 1) & 1; }
    void SetFlags(unsigned int bits, bool set)
    {
        FUN_00017CD0(bits, set);
        if (set) {
            flags |= bits;
        } else {
            flags &= ~bits;
        }
    }
};

// The class that the buy menu, the build menu and the per-player screen 0x00053DD0 derive from. Its
// vtable is at 0x002ED510 and has 31 slots: it overrides slots 0, 1, 2, 4, 5, 11 and 13 of
// UnkTargetBase and adds slots 17 to 30. The constructor takes five arguments, and the class ends
// where the first member of its derived classes begins (F-0100).
class S_00145A00 : public UnkTargetBase
{
public:
    S_00145A00(int a1, int a2, float a3, float a4, float a5);
    virtual ~S_00145A00();
    virtual void FUN_00124940();
    virtual void FUN_00124980(struct ERC* rc);
    virtual void FUN_00017C70(const EVec2* a1);
    virtual void FUN_00017C50(const EVec3* a1);
    virtual void FUN_00017CF0(int a1, int a2, int a3);
    virtual void FUN_001247C0(UnkTargetBase* child);
    virtual void FUN_00145550();
    virtual void FUN_00145D30(int a1);
    virtual void FUN_00145830(int a1, int a2, int a3, int a4);
    virtual void FUN_00146280();
    virtual void FUN_00145B90(int a1);
    virtual void FUN_00145630(int a1);
    virtual void FUN_00145660(int a1, int a2, int a3);
    virtual void FUN_00145680(int a1, int a2, int a3, int a4, int a5);
    virtual void FUN_00145960(int a1);
    virtual void FUN_00053CF0(int a1);
    virtual void FUN_00146240();
    virtual void FUN_00146250();
    virtual void FUN_00145900();
    virtual void FUN_00145940(int a1);

    char unk44[0xF4 - 0x44];
};

// The vtable of Unk802A2AC0 is at 0x002E38F4 and has 3 slots.
class Unk802A2AC0
{
public:
    Unk802A2AC0() { mode = 0; }
    virtual ~Unk802A2AC0() {}
    virtual void SetMode(int newMode) = 0;
    virtual void vfn2(int a1, int a2) = 0;

    int mode;
};

#endif
