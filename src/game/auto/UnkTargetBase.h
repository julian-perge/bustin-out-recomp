#ifndef UNKTARGETBASE_H
#define UNKTARGETBASE_H

// declared: 0x001249C0 UnkTargetBase::UnkTargetBase
// declared: 0x001248B0 UnkTargetBase::~UnkTargetBase

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

    // The destructor destroys this member with the function at 0x00142B90.
    char children[0x0C];
    UnkTargetBase* parent;
    int unk14;
    // The constructor builds this member with the function at 0x00137AF0.
    char text[4];
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
