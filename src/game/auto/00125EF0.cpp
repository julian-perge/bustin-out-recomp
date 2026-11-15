struct Obj_00125EF0
{
    void FUN_00129ea0(int a);
    void FUN_00129f50(int a);
};

extern Obj_00125EF0* DAT_0035d3d8[];

// 0x00125EF0
void __stdcall fn_00125EF0(int index, int a)
{
    DAT_0035d3d8[index]->FUN_00129ea0(a);
}

// 0x00125F10
void __stdcall fn_00125F10(int index, int a)
{
    DAT_0035d3d8[index]->FUN_00129f50(a);
}
