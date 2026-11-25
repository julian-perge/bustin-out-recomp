struct S_001A5FA0;

struct S_001A5FA0_owner
{
    virtual void v0();
    virtual void v1();
    virtual void v2();
    virtual void v3();
    virtual void v4();
    virtual void v5();
    virtual void v6();
    virtual void v7();
    virtual void v8();
    virtual void v9();
    virtual void v10();
    virtual void v11();
    virtual void v12();
    virtual void v13();
    virtual void v14();
    virtual void v15();
    virtual void v16();
    virtual void v17();
    virtual void v18();
    virtual void v19();
    virtual void v20();
    virtual void v21();
    virtual void v22();
    virtual void v23();
    virtual void v24();
    virtual void v25();
    virtual void v26();
    virtual void v27();
    virtual void v28();
    virtual void v29();
    virtual void v30();
    virtual void v31();
    virtual void v32();
    virtual void v33();
    virtual void v34();
    virtual void v35();
    virtual void v36();
    virtual void v37();
    virtual void v38();
    virtual void v39();
    virtual int FUN_slotA0(S_001A5FA0* s);
};

struct S_001A5FA0
{
    char pad0[0x1C];
    int cached;
    char pad1[0x10];
    S_001A5FA0_owner* owner;
    int FUN_001a5fa0();
};

// 0x001A5FA0
int S_001A5FA0::FUN_001a5fa0()
{
    if (cached == 0) {
        owner->FUN_slotA0(this);
    }
    return cached;
}
