struct R_000B0490
{
    int a;
    int b;
};

struct V1_000B0490
{
    int x;
};

struct V2_000B0490
{
    virtual void FUN_v0();
    virtual void FUN_v1();
    virtual void FUN_v2();
    virtual void FUN_v3();
    virtual void FUN_v4();
    virtual void FUN_v5();
    virtual void FUN_v6();
    virtual void FUN_v7();
    virtual void FUN_v8();
    virtual void FUN_v9();
    virtual void FUN_v10();
    virtual void FUN_v11();
    virtual void FUN_v12();
    virtual void FUN_v13();
    virtual void FUN_v14();
    virtual void FUN_v15();
    virtual void FUN_v16();
    virtual void FUN_v17();
    virtual void FUN_v18();
    virtual void FUN_v19();
    virtual void FUN_v20();
    virtual void FUN_v21();
    virtual void FUN_v22();
    virtual void FUN_v23();
    virtual void FUN_v24();
    virtual void FUN_v25();
    virtual void FUN_v26();
    virtual void FUN_v27();
    virtual void FUN_v28();
    virtual void FUN_v29();
    virtual void FUN_v30();
    virtual void FUN_v31();
    virtual void FUN_v32();
    virtual void FUN_v33();
    virtual void FUN_v34();
    virtual void FUN_v35();
    virtual void FUN_v36();
    virtual void FUN_v37();
    virtual void FUN_v38();
    virtual void FUN_v39();
    virtual void FUN_v40();
    virtual void FUN_v41();
    virtual void FUN_v42();
    virtual void FUN_v43();
    virtual void FUN_v44();
    virtual void FUN_v45();
    virtual void FUN_v46();
    virtual void FUN_v47();
    virtual void FUN_v48();
    virtual void FUN_v49();
    virtual void FUN_v50();
    virtual void FUN_v51();
    virtual void FUN_v52();
    virtual void FUN_v53();
    virtual void FUN_v54();
    virtual void FUN_v55();
    virtual void FUN_v56();
    virtual void FUN_v57();
    virtual void FUN_v58();
    virtual void FUN_v59();
    virtual void FUN_v60();
    virtual void FUN_v61();
    virtual void FUN_v62();
    virtual void FUN_v63();
    virtual void FUN_v64();
    virtual void FUN_v65();
    virtual void FUN_v66();
    virtual void FUN_v67();
    virtual void FUN_v68();
    virtual void FUN_v69();
    virtual void FUN_v70();
    virtual void FUN_v71();
    virtual void FUN_v72();
    virtual void FUN_v73();
    virtual void FUN_v74();
    virtual void FUN_v75();
    virtual void FUN_v76();
    virtual void FUN_v77();
    virtual void FUN_v78();
    virtual void FUN_v79();
    virtual void FUN_v80();
    virtual void FUN_v81();
    virtual void FUN_v82();
    virtual void FUN_v83();
    virtual void FUN_v84();
    virtual void FUN_v85();
    virtual void FUN_v86();
    virtual void FUN_v87();
    virtual void FUN_v88();
    virtual void FUN_v89();
    virtual void FUN_v90();
    virtual void FUN_v91();
    virtual void FUN_v92();
    virtual void FUN_v93();
    virtual void FUN_v94();
    virtual void FUN_v95();
    virtual void FUN_v96();
    virtual void FUN_v97();
    virtual void FUN_v98();
    virtual void FUN_v99();
    virtual void FUN_v100();
    virtual void FUN_v101();
    virtual void FUN_v102();
    virtual void FUN_v103();
    virtual void FUN_v104();
    virtual void FUN_v105();
    virtual void FUN_v106();
    virtual void FUN_v107();
    virtual void FUN_v108();
    virtual void FUN_v109();
    virtual void FUN_v110();
    virtual void FUN_v111();
    virtual void FUN_v112();
    virtual R_000B0490* FUN_v113();
};

struct C_000B0490 : virtual V1_000B0490, virtual V2_000B0490
{
    virtual void FUN_c0();
};

struct S_000B0490
{
    int pad;
    C_000B0490* c;
    int FUN_000b0490();
};

// 0x000B0490
int S_000B0490::FUN_000b0490()
{
    return c->FUN_v113()->b;
}
