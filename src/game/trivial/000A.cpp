struct S_000A0C80
{
    int f;
    int FUN_000A0C80();
};
struct S_000A0C90
{
    int* p;
    int FUN_000A0C90();
};
struct S_000A2610
{
    char pad[0x1C];
    int f;
    int FUN_000A2610();
};
void FUN_0015A590();
void FUN_0015A610();
void FUN_00142B90();
void FUN_00123040();
void FUN_001967D0();
struct S_000A4470
{
    int* p;
    int FUN_000A4470();
};
struct S_000A4480
{
    int f;
    int FUN_000A4480();
};
void FUN_00142B50();
struct S_000A8050
{
    char pad[0x368];
    int f;
    int FUN_000A8050();
};
void FUN_00124940();
struct S_000AFDE0
{
    S_000AFDE0();
    virtual ~S_000AFDE0() {}
};
struct S_000AFDF0
{
    virtual ~S_000AFDF0();
};
void FUN_00146EF0();

// 0x000A0C80
int S_000A0C80::FUN_000A0C80()
{
    return f;
}

// 0x000A0C90
int S_000A0C90::FUN_000A0C90()
{
    return p ? p[-1] : 0;
}

// 0x000A2610
int S_000A2610::FUN_000A2610()
{
    return f;
}

// 0x000A28C0
void FUN_000A28C0()
{
    FUN_0015A590();
}

// 0x000A28D0
void FUN_000A28D0()
{
    FUN_0015A610();
}

// 0x000A28E0
void FUN_000A28E0()
{
    FUN_00142B90();
}

// 0x000A3430
void FUN_000A3430()
{
    FUN_00123040();
}

// 0x000A34B0
void FUN_000A34B0()
{
    FUN_001967D0();
}

// 0x000A4470
int S_000A4470::FUN_000A4470()
{
    return p ? p[-1] : 0;
}

// 0x000A4480
int S_000A4480::FUN_000A4480()
{
    return f;
}

// 0x000A8040
void FUN_000A8040()
{
    FUN_00142B50();
}

// 0x000A8050
int S_000A8050::FUN_000A8050()
{
    return f;
}

// 0x000AF7C0
void FUN_000AF7C0()
{
    FUN_00124940();
}

// 0x000AFDE0
S_000AFDE0::S_000AFDE0()
{
}

// 0x000AFDF0
S_000AFDF0::~S_000AFDF0()
{
}

// 0x000AFF90
void FUN_000AFF90()
{
}

// 0x000AFFB0
void FUN_000AFFB0()
{
    FUN_00146EF0();
}
